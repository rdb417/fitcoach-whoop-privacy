#!/usr/bin/env python3
"""Render and check an Industrial AI pre-call tear sheet.

Input is a tearsheet.json content file (see templates/tearsheet.example.json).
Outputs, written next to the JSON unless --out-dir is given:

    <slug>-tearsheet.html   standalone HTML (the print source)
    <slug>-tearsheet.md     portable Markdown version
    <slug>-tearsheet.pdf    one-page PDF (headless Chrome/Chromium, or WeasyPrint)
    <slug>-tearsheet.png    preview image of page 1, for visual inspection

It also runs editorial and evidence checks and prints a report. Exit codes:
    0  rendered, one page, no errors (warnings may still be printed)
    2  content errors (missing sections, not exactly three questions, bad citations)
    3  PDF is not exactly one page (cut content, never shrink fonts)
    4  no PDF engine found (HTML and Markdown were still written)

Only the Python standard library is required. pypdf and Pillow are used when
present for overflow and fill measurements.

Usage:
    python render_tearsheet.py path/to/tearsheet.json [--out-dir DIR]
        [--paper letter|a4] [--check-only] [--no-pdf] [--chrome PATH]
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_HTML = SKILL_DIR / "templates" / "tearsheet.html"
TEMPLATE_MD = SKILL_DIR / "templates" / "tearsheet.md"

BODY_SECTIONS = [
    ("company_product", "A", "Company and product"),
    ("technology", "B", "Technology and differentiation"),
    ("market", "C", "Market and competition"),
    ("team_financing", "D", "Team and financing"),
    ("traction", "E", "Commercial traction"),
]
PERSPECTIVE_KEYS = [
    ("interesting", "What is interesting"),
    ("validate", "What needs validation"),
    ("fit", "{firm} relevance"),
]
SNAPSHOT_KEYS = [
    ("website", "Website"),
    ("headquarters", "Headquarters"),
    ("founded", "Founded"),
    ("stage", "Stage"),
    ("capital_raised", "Capital raised"),
]

WORD_TARGET = (350, 500)
WORD_SOFT_LIMITS = (300, 560)

PROMO_TERMS = [
    "revolutionary", "revolutionize", "game-changing", "game changer", "cutting-edge",
    "cutting edge", "world-class", "best-in-class", "state-of-the-art", "unparalleled",
    "unprecedented", "seamless", "seamlessly", "disruptive", "groundbreaking", "ground-breaking",
    "next-generation", "next-gen", "industry-leading", "market-leading", "leading provider",
    "transformative", "paradigm", "synergy", "robust solution", "powerful platform",
    "unique", "innovative", "visionary", "rockstar", "massive opportunity", "huge market",
]
GENERIC_QUESTION_PATTERNS = [
    r"\bwhat is your (competitive )?(advantage|moat|differentiation)\b",
    r"\btell us (more )?about\b",
    r"\bwhat are your (plans|goals)\b",
    r"\bhow (big|large) is the market\b",
    r"\bwho are your competitors\b",
    r"\bwhat keeps you up at night\b",
    r"\bwhat is your go-to-market\b",
    r"\bhow will you use the (funds|money|capital)\b",
]
FIGURE_RE = re.compile(
    r"(\$|€|£)\s?\d|\b\d[\d,.]*\s?(%|x\b|×|k\b|m\b|bn\b|b\b|million|billion|thousand)",
    re.IGNORECASE,
)
CITE_RE = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]")
TAG_RE = re.compile(r"\{(CR|INF|UNK)\}")


# --------------------------------------------------------------------------- #
# Content helpers
# --------------------------------------------------------------------------- #

def as_blocks(value):
    """Normalise a section value to (paragraphs, bullets)."""
    if value is None:
        return [], []
    if isinstance(value, str):
        return [value], []
    if isinstance(value, list):
        return [], [str(v) for v in value]
    if isinstance(value, dict):
        text = value.get("text") or []
        paras = [text] if isinstance(text, str) else list(text)
        return paras, [str(b) for b in value.get("bullets") or []]
    raise ValueError(f"Unsupported section value: {value!r}")


def section_text(value) -> str:
    paras, bullets = as_blocks(value)
    return " ".join(paras + bullets)


def expand_cites(spec: str) -> list[int]:
    ids: list[int] = []
    for part in re.split(r"\s*,\s*", spec):
        if re.search(r"[–-]", part):
            a, b = re.split(r"\s*[–-]\s*", part)
            ids.extend(range(int(a), int(b) + 1))
        elif part:
            ids.append(int(part))
    return ids


def strip_markup(text: str) -> str:
    text = CITE_RE.sub("", text)
    text = TAG_RE.sub("", text)
    return text.replace("**", "").replace("*", "")


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9$€£][\w$€£%.,'’/&+-]*", strip_markup(text)))


def inline_html(text: str) -> str:
    """Escape, then apply the small markup set: **bold**, *italic*, [n] cites, {CR}/{INF}/{UNK} tags."""
    s = html.escape(str(text), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = CITE_RE.sub(lambda m: f'<sup class="ref">{m.group(1).replace(" ", "")}</sup>', s)
    s = s.replace("{CR}", '<span class="tag cr">CR</span>')
    s = s.replace("{INF}", '<span class="tag inf">INF</span>')
    s = s.replace("{UNK}", '<span class="tag unk">Unknown</span>')
    # Keep a tag or citation on the same line as the word before it.
    s = re.sub(r"\s+(<span class=\"tag|<sup class=\"ref\">)", r"&nbsp;\1", s)
    return s


def inline_md(text: str) -> str:
    s = str(text)
    s = s.replace("{CR}", "*(CR)*").replace("{INF}", "*(INF)*").replace("{UNK}", "*(Unknown)*")
    return s


def blocks_html(value) -> str:
    paras, bullets = as_blocks(value)
    out = [f"<p>{inline_html(p)}</p>" for p in paras]
    if bullets:
        out.append("<ul>" + "".join(f"<li>{inline_html(b)}</li>" for b in bullets) + "</ul>")
    return "".join(out)


def blocks_md(value) -> str:
    paras, bullets = as_blocks(value)
    out = [inline_md(p) for p in paras]
    if bullets:
        out.append("\n".join(f"- {inline_md(b)}" for b in bullets))
    return "\n\n".join(out)


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "company"


def short_url(url: str) -> str:
    u = re.sub(r"^https?://(www\.)?", "", url or "").rstrip("/")
    return u if len(u) <= 58 else u[:55] + "…"


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check(data: dict) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    company = data.get("company") or {}
    meta = data.get("meta") or {}
    sections = data.get("sections") or {}
    perspective = data.get("perspective") or {}
    questions = data.get("questions") or []
    sources = data.get("sources") or []

    if not company.get("name"):
        errors.append("company.name is missing")
    if not company.get("one_liner"):
        errors.append("company.one_liner is missing")
    if not meta.get("research_date"):
        errors.append("meta.research_date is missing (use the date research was performed)")
    if "independent_research" not in meta:
        warnings.append("meta.independent_research not set; state whether live research was possible")
    for key, letter, label in BODY_SECTIONS:
        if not section_text(sections.get(key)).strip():
            errors.append(f"Section {letter} ({label}) is empty: sections.{key}")
    for key, label in PERSPECTIVE_KEYS:
        if not str(perspective.get(key) or "").strip():
            errors.append(f"Perspective '{label.format(firm='Firm')}' is empty: perspective.{key}")
    if len(questions) != 3:
        errors.append(f"Exactly three questions are required, found {len(questions)}")
    for i, q in enumerate(questions, 1):
        qt = q.get("question") if isinstance(q, dict) else str(q)
        if not qt:
            errors.append(f"Question {i} has no text")
            continue
        for pat in GENERIC_QUESTION_PATTERNS:
            if re.search(pat, qt, re.IGNORECASE):
                warnings.append(f"Question {i} reads as generic ('{pat}'); tie it to this company's specifics")
        if isinstance(q, dict) and not q.get("why"):
            warnings.append(f"Question {i} has no 'why' (what the answer would change)")

    # Assemble all prose for text-level checks.
    prose_parts = [company.get("one_liner", "")]
    prose_parts += [section_text(sections.get(k)) for k, _, _ in BODY_SECTIONS]
    prose_parts += [str(perspective.get(k, "")) for k, _ in PERSPECTIVE_KEYS]
    for q in questions:
        if isinstance(q, dict):
            prose_parts += [q.get("question", ""), q.get("why", "")]
        else:
            prose_parts.append(str(q))
    snapshot_text = " ".join(str(company.get(k, "")) for k, _ in SNAPSHOT_KEYS)
    alert_text = str(meta.get("alert") or "")
    prose = "\n".join(prose_parts)
    words = word_count(prose)

    lo, hi = WORD_TARGET
    if words < WORD_SOFT_LIMITS[0] or words > WORD_SOFT_LIMITS[1]:
        warnings.append(f"Body is {words} words; target is {lo}-{hi}")

    # Citations
    source_ids = []
    for s in sources:
        sid = s.get("id")
        if not isinstance(sid, int):
            errors.append(f"Source without integer id: {s}")
            continue
        if sid in source_ids:
            errors.append(f"Duplicate source id {sid}")
        source_ids.append(sid)
        if not (s.get("url") or s.get("note")):
            warnings.append(f"Source [{sid}] has neither url nor note")
    cited: set[int] = set()
    for m in CITE_RE.finditer(prose + " " + snapshot_text + " " + alert_text):
        cited.update(expand_cites(m.group(1)))
    for c in sorted(cited - set(source_ids)):
        errors.append(f"Citation [{c}] has no matching source")
    for u in sorted(set(source_ids) - cited):
        warnings.append(f"Source [{u}] is listed but never cited")
    if not sources:
        warnings.append("No sources listed; every material fact needs a source or an evidence tag")

    # Figures without a citation or evidence tag in the same sentence.
    for sentence in re.split(r"(?<=[.;!?])\s+|\n", prose + "\n" + snapshot_text):
        if FIGURE_RE.search(sentence) and not CITE_RE.search(sentence) and not TAG_RE.search(sentence):
            warnings.append(f"Figure without citation or tag: \"{sentence.strip()[:110]}\"")

    lowered = prose.lower()
    for term in PROMO_TERMS:
        if re.search(r"\b" + re.escape(term) + r"\b", lowered):
            warnings.append(f"Promotional or empty term: '{term}'")
    if "\u2014" in prose or " -- " in prose:
        warnings.append("Em dash or double hyphen found; house style uses commas, colons or parentheses")

    stats = {"words": words, "sources": len(sources), "citations_used": len(cited),
             "cr_tags": prose.count("{CR}"), "inf_tags": prose.count("{INF}"),
             "unk_tags": prose.count("{UNK}")}
    return errors, warnings, stats


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def fill(template: str, values: dict) -> str:
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values.get(m.group(1), "")), template)


def meeting_line(meta: dict) -> str:
    parts = [meta.get("meeting"), meta.get("meeting_date")]
    return " · ".join(p for p in parts if p)


def research_line(meta: dict) -> str:
    basis = meta.get("research_basis")
    if not basis:
        basis = ("Independent web research plus supplied materials"
                 if meta.get("independent_research", True)
                 else "Supplied materials only; not independently verified")
    line = f"Research date {meta.get('research_date', 'n/a')} · {basis}"
    if meta.get("analyst"):
        line += f" · {meta['analyst']}"
    return line


def render_html(data: dict, paper: str) -> str:
    company, meta = data["company"], data.get("meta", {})
    firm = meta.get("firm", "Leitmotif")
    sections, perspective = data.get("sections", {}), data.get("perspective", {})

    snapshot = "".join(
        f'<div class="cell"><div class="k">{label}</div><div class="v">{inline_html(company.get(key) or "Not disclosed")}</div></div>'
        for key, label in SNAPSHOT_KEYS
    )
    alert = ""
    if meta.get("alert"):
        alert = f'<div class="alert"><b>Read first.</b> {inline_html(meta["alert"])}</div>'
    elif meta.get("independent_research") is False:
        alert = ('<div class="alert"><b>Read first.</b> Live research was not available. This briefing '
                 'relies on supplied materials and has not been independently verified.</div>')

    body = "".join(
        f'<div class="sec"><h2><span class="letter">{letter}</span>{label}</h2>{blocks_html(sections.get(key))}</div>'
        for key, letter, label in BODY_SECTIONS
    )
    persp = "".join(
        f'<div><h3>{label.format(firm=html.escape(firm))}</h3><p>{inline_html(perspective.get(key, ""))}</p></div>'
        for key, label in PERSPECTIVE_KEYS
    )
    qs = []
    for q in data.get("questions", []):
        if isinstance(q, dict):
            why = f' <span class="why">{inline_html(q["why"])}</span>' if q.get("why") else ""
            qs.append(f'<li><span class="q">{inline_html(q.get("question", ""))}</span>{why}</li>')
        else:
            qs.append(f'<li><span class="q">{inline_html(q)}</span></li>')

    src = []
    for s in data.get("sources", []):
        bits = [html.escape(b) for b in (s.get("publisher"), s.get("title")) if b]
        label = ", ".join(bits)
        if s.get("date"):
            label += f" ({html.escape(str(s['date']))})"
        if s.get("note"):
            label += f". {html.escape(s['note'])}"
        url = s.get("url")
        link = f' <a class="u" href="{html.escape(url)}">{html.escape(short_url(url))}</a>' if url else ""
        src.append(f'<div><span class="n">{s.get("id")}</span>{label}{link}</div>')

    values = {
        "title": html.escape(f"{company.get('name', 'Company')} | {firm} tear sheet"),
        "page_size": "A4" if paper == "a4" else "Letter",
        "firm": html.escape(firm),
        "prepared_for": html.escape(meta.get("prepared_for", "Partner briefing")),
        "meeting_line": html.escape(meeting_line(meta)),
        "company_name": html.escape(company.get("name", "")),
        "one_liner": inline_html(company.get("one_liner", "")),
        "snapshot": snapshot,
        "alert": alert,
        "body_sections": body,
        "perspective": persp,
        "questions": "".join(qs),
        "research_line": html.escape(research_line(meta)),
        "sources": "".join(src),
    }
    return fill(TEMPLATE_HTML.read_text(encoding="utf-8"), values)


def render_md(data: dict) -> str:
    company, meta = data["company"], data.get("meta", {})
    firm = meta.get("firm", "Leitmotif")
    sections, perspective = data.get("sections", {}), data.get("perspective", {})
    alert = ""
    if meta.get("alert"):
        alert = f"> **Read first.** {inline_md(meta['alert'])}"
    elif meta.get("independent_research") is False:
        alert = "> **Read first.** Live research was not available. This briefing relies on supplied materials and has not been independently verified."
    qs = []
    for i, q in enumerate(data.get("questions", []), 1):
        if isinstance(q, dict):
            why = f" *{inline_md(q['why'])}*" if q.get("why") else ""
            qs.append(f"{i}. **{inline_md(q.get('question', ''))}**{why}")
        else:
            qs.append(f"{i}. **{inline_md(q)}**")
    src = []
    for s in data.get("sources", []):
        label = ", ".join(b for b in (s.get("publisher"), s.get("title")) if b)
        if s.get("date"):
            label += f" ({s['date']})"
        if s.get("note"):
            label += f". {s['note']}"
        url = f" <{s['url']}>" if s.get("url") else ""
        src.append(f"{s.get('id')}. {label}{url}")
    values = {
        "company_name": company.get("name", ""),
        "firm": firm,
        "prepared_for": meta.get("prepared_for", "Partner briefing"),
        "meeting_line": meeting_line(meta),
        "one_liner": inline_md(company.get("one_liner", "")),
        "alert": alert,
        "research_line": research_line(meta),
        "interesting": inline_md(perspective.get("interesting", "")),
        "validate": inline_md(perspective.get("validate", "")),
        "fit": inline_md(perspective.get("fit", "")),
        "questions": "\n".join(qs),
        "sources": "\n".join(src),
    }
    for key, _ in SNAPSHOT_KEYS:
        values[key] = inline_md(company.get(key) or "Not disclosed").replace("|", "/")
    for key, _, _ in BODY_SECTIONS:
        values[key] = blocks_md(sections.get(key))
    md = fill(TEMPLATE_MD.read_text(encoding="utf-8"), values)
    return re.sub(r"\n{3,}", "\n\n", md)


# --------------------------------------------------------------------------- #
# PDF engines and measurement
# --------------------------------------------------------------------------- #

CHROME_CANDIDATES = [
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome",
    "microsoft-edge", "msedge",
    "/opt/pw-browsers/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_chrome(explicit: str | None) -> str | None:
    for cand in [explicit, os.environ.get("CHROME_PATH")] + CHROME_CANDIDATES:
        if not cand:
            continue
        path = shutil.which(cand) or (cand if os.path.isfile(cand) else None)
        if path:
            return path
    pw = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", Path.home() / ".cache" / "ms-playwright"))
    for p in sorted(pw.glob("chromium-*/chrome-*/chrome"), reverse=True):
        return str(p)
    return None


def chrome_flags() -> list[str]:
    flags = ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
             "--no-default-browser-check", "--disable-extensions"]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        flags.append("--no-sandbox")
    return flags


def run_chrome(cmd: list[str], expected: Path, timeout: int = 60) -> None:
    """Run headless Chrome; some builds keep running after writing output, so accept the file if present."""
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    if not expected.exists() or expected.stat().st_size == 0:
        raise RuntimeError(f"Chrome produced no output at {expected}")


def pdf_with_chrome(chrome: str, html_path: Path, pdf_path: Path) -> None:
    if pdf_path.exists():
        pdf_path.unlink()
    # Note: passing --user-data-dir makes some Chromium builds hang after printing.
    run_chrome([chrome, *chrome_flags(), "--no-pdf-header-footer", "--print-to-pdf-no-header",
                f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()], pdf_path)


def pdf_with_weasyprint(html_path: Path, pdf_path: Path) -> None:
    from weasyprint import HTML  # type: ignore
    HTML(filename=str(html_path)).write_pdf(str(pdf_path))


def count_pages(pdf_path: Path) -> int:
    try:
        from pypdf import PdfReader  # type: ignore
        return len(PdfReader(str(pdf_path)).pages)
    except ImportError:
        pass
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.MULTILINE)
        if m:
            return int(m.group(1))
    return len(re.findall(rb"/Type\s*/Page(?!s)", pdf_path.read_bytes()))


def overflow_words(pdf_path: Path) -> int | None:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None
    pages = PdfReader(str(pdf_path)).pages
    return sum(len((p.extract_text() or "").split()) for p in pages[1:])


def make_preview(pdf_path: Path, html_path: Path, png_path: Path, chrome: str | None) -> bool:
    if shutil.which("pdftoppm"):
        prefix = png_path.with_suffix("")
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", "1", "-l", "1", "-singlefile",
                        str(pdf_path), str(prefix)], check=False)
        if png_path.exists():
            return True
    if chrome:
        try:
            run_chrome([chrome, *chrome_flags(), "--window-size=900,1200", f"--screenshot={png_path}",
                        html_path.resolve().as_uri()], png_path)
        except RuntimeError:
            return False
        return png_path.exists()
    return False


def page_fill(png_path: Path) -> float | None:
    """Fraction of the page height that holds content (bottom of last non-white row)."""
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return None
    img = Image.open(png_path).convert("L")
    w, h = img.size
    px = img.load()
    for y in range(h - 1, -1, -1):
        if any(px[x, y] < 235 for x in range(0, w, 3)):
            return round((y + 1) / h, 3)
    return 0.0


# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("content", type=Path, help="tearsheet.json")
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--paper", choices=["letter", "a4"], default="letter")
    ap.add_argument("--check-only", action="store_true", help="run content checks only")
    ap.add_argument("--no-pdf", action="store_true", help="write HTML and Markdown only")
    ap.add_argument("--chrome", help="path to a Chrome/Chromium/Edge binary")
    args = ap.parse_args()

    data = json.loads(args.content.read_text(encoding="utf-8"))
    errors, warnings, stats = check(data)

    print(f"Content: {stats['words']} words (target {WORD_TARGET[0]}-{WORD_TARGET[1]}), "
          f"{stats['sources']} sources, {stats['citations_used']} cited, "
          f"tags CR={stats['cr_tags']} INF={stats['inf_tags']} Unknown={stats['unk_tags']}")
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    if args.check_only:
        return 2 if errors else 0
    if errors:
        print("Fix the errors above before rendering.")
        return 2

    out_dir = args.out_dir or args.content.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{slugify(data['company']['name'])}-tearsheet"
    html_path, md_path = out_dir / f"{stem}.html", out_dir / f"{stem}.md"
    pdf_path, png_path = out_dir / f"{stem}.pdf", out_dir / f"{stem}.png"

    html_path.write_text(render_html(data, args.paper), encoding="utf-8")
    md_path.write_text(render_md(data), encoding="utf-8")
    print(f"Wrote {html_path}")
    print(f"Wrote {md_path}")
    if args.no_pdf:
        return 0

    chrome = find_chrome(args.chrome)
    engine = None
    try:
        if chrome:
            pdf_with_chrome(chrome, html_path, pdf_path)
            engine = "chrome"
    except Exception as exc:  # fall through to WeasyPrint
        print(f"WARNING Chrome PDF failed: {exc}")
    if engine is None:
        try:
            pdf_with_weasyprint(html_path, pdf_path)
            engine = "weasyprint"
        except Exception:
            print("No PDF engine available (install Chrome/Chromium or `pip install weasyprint`).")
            print("Deliver the HTML (print to PDF from a browser) and the Markdown instead.")
            return 4

    pages = count_pages(pdf_path)
    print(f"Wrote {pdf_path} ({engine}, {pages} page{'s' if pages != 1 else ''})")
    if make_preview(pdf_path, html_path, png_path, chrome):
        fill_ratio = page_fill(png_path)
        print(f"Wrote {png_path}" + (f" (content reaches {fill_ratio:.0%} of page height)" if fill_ratio is not None else ""))
        if fill_ratio is not None and pages == 1 and fill_ratio < 0.80:
            print("NOTE    Page is under-filled; there is room for one more high-value point if the evidence supports it.")
    if pages != 1:
        extra = overflow_words(pdf_path)
        hint = f" (~{extra} words spill past page 1)" if extra else ""
        print(f"FAIL    PDF has {pages} pages{hint}. Cut lower-priority content; do not shrink fonts.")
        return 3
    print("OK      One page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

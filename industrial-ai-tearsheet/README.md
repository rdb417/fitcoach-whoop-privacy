# Industrial AI Pre-Call Tear Sheet (Leitmotif)

A Claude skill that prepares a one-page, evidence-tagged briefing on an industrial AI or deep-tech startup ahead of an introductory pitch call. It researches the company independently, explains the technology, places commercial claims on a pilot-to-production ladder, maps the relevant competitors, forms a preliminary investment hypothesis, and writes three company-specific questions for the meeting.

Output per company: a one-page PDF, editable Markdown and HTML, the source content (`tearsheet.json`), an evidence register, and research notes for later diligence.

## Install

**Claude (web or desktop app):** zip the `industrial-ai-tearsheet` folder (or use the packaged `industrial-ai-tearsheet.skill` file) and upload it in Settings under Skills / Capabilities. Code execution must be enabled for PDF rendering. The exact menu location may differ by plan and app version.

**Claude Code:** copy the folder to `~/.claude/skills/industrial-ai-tearsheet/` (personal) or `.claude/skills/industrial-ai-tearsheet/` inside a project (shared with the team via git).

**Requirements for PDF output:** Python 3.9+ and either Google Chrome / Chromium / Microsoft Edge (detected automatically, or set `CHROME_PATH`) or `pip install weasyprint`. Without either, the skill still produces HTML (print to PDF from any browser) and Markdown. `pypdf` and `Pillow` are optional and add overflow and page-fill measurements.

## Use

Ask in plain language, for example:

> Create a pre-call industrial AI tear sheet for Fero Labs. Website: ferolabs.com.

> Prepare a one-page Leitmotif briefing for this company ahead of our introductory call. I've attached their pitch deck.

Optional context improves the result: founder names, the meeting email, the partners' specific questions, prior notes, meeting date and attendees. Claude does not need these to start.

For A4 output, say "A4" in the request.

## Customize for the team

- `references/firm-context.md` holds Leitmotif's public profile, a partial portfolio list, and the rules for when to mention Volkswagen Group relevance. **Update it** with the current thesis and full portfolio so the "Leitmotif relevance" line and conflict checks are accurate.
- `templates/tearsheet.html` controls the look. Colors are CSS variables at the top.
- `references/editorial-standards.md` sets voice, word budget, and the cut order when content runs long.

## Re-render after editing

Edit the saved `tearsheet.json` and run:

```bash
python3 scripts/render_tearsheet.py path/to/tearsheet.json --out-dir path/to/folder [--paper a4]
```

The script checks content (three questions, citations resolve, uncited figures, promotional language), renders HTML, Markdown, PDF and a PNG preview, and fails if the PDF is not exactly one page.

## Layout

```
industrial-ai-tearsheet/
├── SKILL.md                        workflow and standards (loaded when the skill triggers)
├── references/
│   ├── research-standards.md       identity, research plan, sources, evidence classes
│   ├── industrial-ai-framework.md  deployment dimensions, maturity ladder, archetype lenses
│   ├── investment-assessment.md    seven questions, validation ladder, question design
│   ├── firm-context.md             Leitmotif profile, portfolio, VW relevance rules (edit me)
│   └── editorial-standards.md      voice, word budget, cut order, QA checklist
├── templates/
│   ├── tearsheet.html              one-page print layout
│   ├── tearsheet.md                Markdown layout
│   └── tearsheet.example.json      content schema by example (fictional company)
├── scripts/render_tearsheet.py     render + checks + one-page validation (stdlib only)
├── tests/evaluation-cases.md       rubric and test plan
├── evals/                          machine-runnable test cases
└── examples/                       sample output
```

## Limits

- Research quality depends on the tools available in the environment (web search, page fetch, connected databases such as PitchBook). If browsing is unavailable, the sheet says so in a banner.
- The briefing is a pre-meeting hypothesis, not diligence. Verify any fact you intend to rely on.

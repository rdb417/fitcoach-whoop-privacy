# Editorial Standards

Read this before drafting `tearsheet.json`. The reader is a technically fluent investment partner with three minutes before a call.

## Voice

- Analytical, measured, specific. Write as an analyst briefing a partner, not as the company describing itself.
- Lead with the mechanism or the fact, not with adjectives. "Learns new weld variants from ~40 labeled images {CR}" beats "an innovative few-shot platform".
- Prefer plain technical terms over buzzwords. Explain a niche term in a few words the first time if a generalist partner might not know it (e.g., "VLA (vision-language-action) model").
- Use commas, colons, periods or parentheses instead of em dashes or double hyphens (house style).
- No promotional language: revolutionary, cutting-edge, world-class, seamless, unique, innovative, leading, game-changing, best-in-class, disruptive, massive opportunity. The renderer warns on these.

## Word budget

Target 350 to 500 words for the body (sources excluded); in practice 380 to 460 words with up to about 9 sources fills one page well. The source list takes real space: each source is one or two lines. Approximate allocation:

| Part | Words |
|---|---|
| One-liner | 20-30 |
| A. Company and product | 45-70 |
| B. Technology and differentiation | 70-100 |
| C. Market and competition | 60-90 |
| D. Team and financing | 50-80 |
| E. Commercial traction | 35-65 |
| F. Perspective (three parts) | 70-100 |
| G. Questions (with one-line why) | 60-90 |

Spend words where the investment view is decided. If the technology is the whole story, B gets more; if the company is a commercial execution story, E gets more.

## The one-liner

One sentence: what the company does, for whom, and why it matters. It should still be accurate if a skeptic read it. Example shape: "[Does X] for [buyer/workflow], [the economic or technical reason it matters]."

## Evidence markup

- `[n]` after a fact cites source n. Multiple: `[2,5]`.
- `{CR}` after a company-reported claim, `{INF}` after your inference, `{UNK}` on a gap.
- Put the tag right after the claim it qualifies, not at the end of a long sentence covering several claims.
- Every figure (money, %, counts, multiples) needs a citation or a tag. The renderer flags uncited figures.
- Do not over-tag. Two to six `{CR}`, two to six `{INF}` and one to four `{UNK}` is a typical healthy sheet. Many `{CR}` tags on one sheet is itself a finding: say in E or F that the evidence is mostly company-reported.

## Structure and density

- Short paragraphs and bullets of one or two lines. Bold the lead phrase of a bullet sparingly (competitor names, "Claimed edge:", "Likely moat:").
- Competitors in C: two to four bullets, each "**Name**: what they do; how the target differs."
- Snapshot fields: short values ("$18M (seed + A)", "Munich, DE", "2023"). Use "Not disclosed" rather than leaving a field blank. Add `{CR}` or `[n]` if the value is uncertain or contested.
- Use `meta.alert` for anything a partner must know before reading the rest: ambiguous identity, an acquisition or pivot, conflicting funding data, supplied-materials-only research, very limited public information. Keep it to one or two sentences.

## Bad to good rewrites

| Weak | Better |
|---|---|
| "XYZ is a leading AI company revolutionizing manufacturing with its proprietary platform." | "XYZ sells vision software that flags machining defects at the spindle, aimed at aerospace job shops where scrap is expensive." |
| "The team is highly experienced." | "CEO ran quality at a 400-person machining supplier [4]; CTO's PhD work on 3D defect detection is cited in the product docs [5]." |
| "The market is huge ($500B+)." | "Initial buyer is the plant quality lead; budget usually comes from capex for new lines, which slows sales outside launch windows {INF}." |
| "They have strong traction with Fortune 500 customers." | "Website shows five OEM logos {CR}; one (Bosch) is confirmed by a customer-side case study [6]. Revenue not disclosed {UNK}." |
| "Risk: competition." | "Cognex added few-shot deep-learning tools in its current product line [7]; the edge must come from weld-specific data, which is unproven at scale {INF}." |

## When content does not fit on one page

Cut in this order, re-rendering after each cut:
1. Background or history that does not affect the investment view.
2. Redundancy between sections (the same point in A, B and F).
3. Secondary competitors and expansion-market speculation.
4. Detail inside bullets (keep the claim, drop the elaboration).
5. Fewer sources: merge sources from the same publisher (one PitchBook entry covering profile, deals and investors), drop ones that only repeat a stronger source, and shorten titles to about six words. Then run `--renumber`.

The body columns balance automatically (sections can flow across the column break), so a cut anywhere in sections A to E shortens the page. If the renderer says page 2 starts inside the sources, trim sources before cutting analysis.

Never shrink fonts, margins or line spacing to fit. Never drop the three questions, the evidence tags, or the alert.

## When the page is under-filled

If the renderer reports content reaching less than about 80% of the page and you have strong evidence you cut, add back the highest-value point (usually a technical mechanism detail, a commercial evidence detail, or a sharper risk). Do not add filler.

## QA checklist before delivering

- [ ] Company identity confirmed by at least two anchors, or the alert explains the ambiguity.
- [ ] Every company-specific fact has `[n]` or a tag; every figure is cited or tagged.
- [ ] Funding figures checked against the strongest available source; conflicts explained.
- [ ] Commercial claims placed on the validation ladder (logo, LOI, pilot, production, recurring); no revenue inferred from logos.
- [ ] Technology section names the mechanism and the most plausible source of defensibility, not just "proprietary AI".
- [ ] Two to four competitors or alternatives, each confirmed to exist and target the same workflow.
- [ ] Section F follows from the evidence above it; Volkswagen mentioned only if there is a concrete workflow match.
- [ ] Exactly three questions, each specific to this company, each with a one-line why.
- [ ] Research date set; `research_access` accurate (full, search_only, none).
- [ ] Renderer reports one page and no errors; preview image inspected for clipping, awkward breaks and balance.

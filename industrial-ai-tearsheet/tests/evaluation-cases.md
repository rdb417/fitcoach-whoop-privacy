# Evaluation Cases

How to tell whether the skill produces briefings an experienced deep-tech investor would read before a first meeting. Machine-runnable versions of the cases live in `../evals/` (one folder per case, in the layout `claude plugin eval` reads). This file is the human-readable rubric.

## How to run

**By hand (any environment):** start a fresh conversation with the skill installed, paste a case prompt, and score the output against the rubric below.

**Claude Code CLI (optional):** from the skill directory, `claude plugin eval . --allow-tools Write,Edit,Bash,WebSearch,WebFetch --scaffold`. Each case is run with and without the skill. These are real, billed model runs with live web research, so expect several minutes per case.

**Renderer only (no model):** `python3 scripts/render_tearsheet.py templates/tearsheet.example.json --out-dir /tmp/ts-check` should print `OK One page.`

## Cases

| Case folder | Archetype / failure mode | What it tests |
|---|---|---|
| `noetive-requested-example` | Early-stage company, name-only input | Identity resolution, honest handling of thin public data |
| `cv-inspection-instrumental` | 1. Computer vision inspection | Explaining the inspection stack; logos vs confirmed deployments; incumbent vision alternatives |
| `robotics-fm-skild` | 2. Robotics foundation model | Separating demos from deployed performance; data and embodiment story; business model |
| `process-optimization-fero` | 3. Process optimization software | Plant data integration; APC incumbents; ROI claims tagged correctly |
| `autonomous-mfg-machina` | 4. Autonomous manufacturing | Vendor vs manufacturer business model; capital intensity; contract evidence |
| `limited-info-unverified-deck` | Limited public info + unverified claims + undisclosed investors | Uses the deck, tags every claim CR, prominent alert, no invented facts |

Failure modes still worth adding as the team uses the skill: an ambiguous company name with no URL, a company recently acquired or pivoted, and two sources with conflicting funding totals.

## Rubric

Score each dimension Pass / Partial / Fail. A briefing worth sending passes all of the first four and at least five of the remaining six.

| Dimension | Pass looks like |
|---|---|
| Factual accuracy | Spot-check five material facts (founders, funding, investors, a customer, founding year) against the cited sources; all match. No invented customers, competitors, or numbers. |
| Evidence labeling | Company-only claims carry CR; inferences carry INF; gaps are marked Unknown; every figure is cited or tagged. |
| Commercial judgment | Distinguishes logos, partnerships, pilots, production deployments and recurring revenue; no revenue inferred from logos. |
| Presentation | Exactly one page, legible at normal size, no clipping, consistent layout. |
| Technical depth | Explains how the system works and names the most plausible source of defensibility, beyond "proprietary AI". |
| Industrial understanding | Picks the deployment factors that matter for this company (integration, robustness, deployment burden, autonomy level) and skips irrelevant ones. |
| Competitive insight | Two to four real, relevant alternatives, including the incumbent or build-in-house path where relevant. |
| Investment relevance | Section F follows from the evidence; risks are specific; Leitmotif fit is honest; no manufactured Volkswagen link. |
| Meeting preparation | Three questions that a weak and a strong company would answer differently, each tied to a real unknown. |
| Editorial quality | Reads like an analyst, not a website summary. No promotional language. 350-500 words. |

## Quick fact-check procedure

1. Open `evidence-register.md`. Pick the five claims a partner is most likely to repeat in the meeting.
2. Open each cited source. Confirm the claim and the class (verified vs company-reported).
3. Search once for the company name plus "acquired", "raises", and "layoffs" to catch status changes the briefing may have missed.
4. Record misses here with the date, so the skill's references can be improved.

## Results log

| Date | Case | Result | Notes |
|---|---|---|---|
| 2026-10-23 | all six cases | see iteration-1 summary in the build notes | First iteration run during skill development |

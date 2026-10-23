# Preliminary Investment Assessment

Use this to turn research into a balanced pre-call hypothesis and three high-value questions. The output is a hypothesis to test in the meeting, not a recommendation. No scores.

## Contents
1. The seven questions
2. Commercial validation ladder
3. Business model patterns and what they imply
4. Team assessment
5. Risk taxonomy
6. Prioritizing unknowns
7. Designing the three questions
8. Writing section F

---

## 1. The seven questions

Answer each briefly in your working notes. Only the strongest one or two answers reach the sheet.

| Question | What good evidence looks like | Weak or generic answer to avoid |
|---|---|---|
| **Why now?** | A specific enabler: a model capability (VLA models, cheap edge inference), a cost curve (sensors, robot arms), a labor or regulatory shift (skilled-labor shortage, EU Machinery Regulation, reshoring incentives, energy prices), or a customer budget that just opened | "AI is advancing rapidly" |
| **Why this team?** | Founders who did this job in industry, built a comparable system before, or have rare research credentials in the core method, plus evidence of shipping | "Experienced team" |
| **Why this technology?** | A named mechanism and why competitors cannot easily copy it (see framework §5) | "Proprietary AI platform" |
| **Why this market?** | A buyer with budget, a measurable pain, and a path from wedge to a venture-scale outcome (multiple sites, verticals, or product lines) | "$X trillion manufacturing market" |
| **Why might it win?** | A compounding advantage: data flywheel, installed-base expansion, deployment speed, channel | "First mover" |
| **Why might it fail?** | The specific technical, commercial, capital, or competitive risk most likely to kill it | "Execution risk" |
| **Why Leitmotif?** | Fit with the firm's thesis and portfolio (see `firm-context.md`), and any genuine industrial relevance | A manufactured Volkswagen link |

## 2. Commercial validation ladder

Classify every commercial claim. They are not interchangeable, and the sheet should say which rung each customer is on.

1. Logo on website or "working with" language: no evidentiary value on its own.
2. Announced partnership, MOU, or LOI: intent only.
3. Unpaid POC or design partnership.
4. Paid pilot.
5. Signed production contract.
6. Production deployment in daily use.
7. Multi-site or multi-line expansion at the same customer.
8. Recurring revenue at scale with renewal history.

Rules:
- Never infer revenue from customer logos, partnerships, or headcount.
- "Deployed at X" is company-reported unless the customer says so.
- Revenue, ARR, and customer counts from a deck are `{CR}`. Say what the metric is (ARR vs bookings vs contracted value) if the deck is ambiguous, and flag it for the call.
- Grants and government contracts are real money but not product-market fit evidence by themselves.

## 3. Business model patterns and what they imply

| Model | Typical gross margin direction | What to check |
|---|---|---|
| Software subscription (per line, site, asset, or seat) | High | How much services is bundled to make it work |
| Hardware plus software | Mixed, depends on hardware share | Who builds hardware, BOM cost trend, attach rate of software |
| Robots-as-a-service | Mixed, capital intensive | Who owns the asset, utilization, financing |
| Outcome or gain-share pricing | Potentially high, volatile | Measurement and attribution disputes |
| Project-based or NRE heavy | Lower, services-like | Whether NRE declines per deployment |
| Operating own factory / selling parts | Manufacturing margins | Whether a software multiple is justified at all |
| Model licensing / API (robotics foundation models) | Uncertain | Who the paying customer is, and whether incumbents build their own |

Margin directions are general patterns, not facts about the company. Only state the company's margin if disclosed (and tag it).

## 4. Team assessment

Look for the credentials that matter for *this* company's hardest problem:
- **Industrial domain**: ran a line, plant, quality function, process engineering group, or sold to these buyers. This shortens sales cycles and avoids naive product decisions.
- **Core technical**: published or shipped the specific method (VLA models, 3D vision, RL for control, robotics hardware). Check publications and prior systems, not titles.
- **Deployment and commercial**: someone who has run field deployments or enterprise industrial sales.
- **Prior outcomes**: earlier startups, exits, or notable failures (both are informative).

State facts and their relevance ("CTO led perception at X's warehouse robots, which shipped to Y sites [n]"). Avoid adjectives about founder quality. Name a team gap only when the evidence clearly shows it (e.g., no one with industrial sales experience at a company whose risk is enterprise sales), and phrase it as something to validate.

## 5. Risk taxonomy

Pick the one or two that matter most:
- **Technical**: does it work reliably in production conditions; does performance generalize across sites and variants.
- **Deployment**: engineering effort per site does not fall; pilot purgatory.
- **Commercial**: long sales cycles, budget owner unclear, ROI not provable, small initial wedge.
- **Competitive**: incumbent bundling, hyperscaler or model-lab entry, a better-funded direct competitor.
- **Capital**: hardware or data collection costs outrun financing; heavy dependence on one strategic investor or customer.
- **Platform dependency**: reliance on a single robot OEM, model provider, or integrator.
- **Concentration**: one customer or one vertical is most of the evidence.

## 6. Prioritizing unknowns

List the open questions, then rank by: *if we learned the answer, how much would our view change?* An unknown that would move the company from "interesting" to "pass" or from "interesting" to "priority" outranks one that only refines the picture. The top three become the call questions; the next one or two become "What needs validation" in section F.

## 7. Designing the three questions

Each question should:
- Be answerable in a first meeting (founders know the answer).
- Target the biggest unknown for this company, not a generic VC theme.
- Ask for specifics that are hard to spin: numbers, named examples, the last instance of something, what went wrong.
- Discriminate between a decent company and an exceptional one: a weak company and a strong one would answer it differently.

Weak versus strong:

| Weak (generic) | Strong (discriminating) |
|---|---|
| What is your competitive advantage? | When the second Tier 1 plant came online, what did you reuse from the first and what did you rebuild? |
| How big is the market? | Which budget line pays for this at the plant, and who signed the last PO? |
| Tell us about your traction. | Of the four pilots announced last year, which are now in production, and what killed the others? |
| How does your model work? | How many hours of task-specific teleop data did the last new task need, and how has that number moved? |
| What are your plans for the funding? | What is the next technical milestone that changes the deployment cost curve, and what does it cost to reach? |

Add a short `why` for each: what the answer would tell the partner. Keep it to one line.

## 8. Writing section F

- **What is interesting**: one or two points, each tied to evidence on the sheet. The best version names the mechanism of advantage and the condition under which it holds.
- **What needs validation**: one or two risks that the research could not resolve and that would most change the view.
- **Firm relevance**: why this fits (or only partly fits) the firm's thesis, portfolio adjacency or overlap, and any industrial relevance that is concrete. If fit is weak, say so; it is useful information.

Write these as an analyst briefing a partner: direct, specific, and comfortable with uncertainty. "Interesting if X; we do not yet know Y" is a good shape.

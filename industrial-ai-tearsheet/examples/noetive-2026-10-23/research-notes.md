# Research notes: Noetive (noetive.ai)

Research date 2026-10-23 · Leitmotif intro call with founders, week of 2026-10-26 · Companion to `tearsheet.json` and `evidence-register.md`.

## 1. Identity resolution

- **Anchors used:** (1) the domain www.noetive.ai on PitchBook profile 1497563-29 (legal name Noetive AI Inc.); (2) founders Amir Frenkel (CEO) and Dan Barak (CPO), named in PitchBook and independently in SiliconANGLE and in Craft Ventures' own post; (3) Sidley's announcement as company counsel names "Noetive AI Inc." and the $41M seed. All three agree.
- **Name collisions to avoid:** Noetica AI (deal-term benchmarking for law firms, CEO Dan Wertman) and Noem.ai are unrelated. Another "Dan Barak" (Text Blaze) also exists.
- **HQ conflict:** PitchBook gives Los Altos, CA (11120 Mora Drive). Press and aggregators say San Francisco. Not material, but worth a quick confirmation.
- **Status:** emerged from stealth 2026-09-16. No pivot, acquisition or departure found.

## 2. Research limits

- WebFetch returned DNS failures (ENOTFOUND) for every domain tried, including noetive.ai. Direct curl was blocked by the proxy (CONNECT 403). **The company website was never read directly.**
- The PitchBook connector worked. Its news tool returned verbatim excerpts of SiliconANGLE (2026-09-16), Craft Ventures (2026-10-06) and the Grishin Robotics newsletter. These are the strongest article-level sources.
- Everything else rests on web search result text, labelled "search snippet" in the register.
- About 30 searches and connector calls in total.

## 3. Archetype and framework

- **Primary lens:** 4c process optimization and industrial analytics (planning and decision layer over ERP and plant data), with a 4f industrial agents flavour. Hardware sensing (the pod) adds a 4e/4g-like data-capture element.
- **Dimensions that decide this company:**
  1. **Integration and human involvement:** does it read only, or write plans back to ERP or MES? Who signs off? Closed-loop write-back is a much higher bar (and much stickier).
  2. **Deployment burden:** engineer-days per site. Forward-deployed engineering (the Palantir model) can look like product at the design-partner stage.
  3. **Scalability across sites and verticals:** the "self-improving" thesis only matters if learning transfers between customers. Manufacturing, logistics, energy, data centers and construction are five different data worlds.
  4. **Sensing pod economics:** whether own hardware is necessary for the value or a drag on rollout.
- **Maturity ladder:** Steuben is at rung 3 at best (design partner, possibly paid, given PitchBook's "Generating Revenue" field). Production use is claimed by the customer quote ("now happens daily") but scope and vendor involvement are unknown. No multi-site evidence.
- **Likely real differentiation {INF}:** not the model. If anything, a cross-customer dataset that joins plans, outcomes and floor signals, plus workflow lock-in once planners rely on daily plans. The pod is a bet that floor-level data (not in ERP) is the missing input. It would be disproved if the Steuben gain comes mostly from ERP data plus good optimization or LLM agents, with the pod contributing little.

## 4. Seven questions (working notes)

- **Why now?** LLM-based agents can now operate over messy enterprise systems; cheap multimodal sensing; labor scarcity in planning roles. Eclipse raised $1.3B in April 2026 explicitly to "back and build" physical AI companies, and Noetive is one of the first visible builds.
- **Why this team?** Strong AI and product-scaling credentials (Meta VP across GenAI and XR, Google Glass, Amazon devices; Barak built and sold Stackbit). A 20+ year founder relationship (per Craft). **Gap:** no disclosed plant, supply-chain or logistics operating experience among the founders. The angel list is consumer and AI-tech heavy (Meta, Airbnb, Nest, Decart) rather than industrial.
- **Why this technology?** Unclear. No papers, patents or docs. The mechanism is described only at the level of a "brain plus agents plus pod".
- **Why this market?** Production planning and scheduling is a real, budgeted pain (Kinaxis, o9, SAP IBP and Palantir all sell into it). Mid-size process manufacturers like Steuben are often underserved by heavy APS suites. The path to venture scale is horizontal expansion across operations decisions, which is also the biggest focus risk.
- **Why might it win?** If learning compounds across deployments and the pod creates data that competitors working from ERP alone lack, plus a well-capitalized incubator with an ecosystem of portfolio companies as potential design partners.
- **Why might it fail?** (a) It becomes a forward-deployed services business per site; (b) vertical sprawl at five months old; (c) Palantir AIP, Kinaxis agents and SAP bundling squeeze the planning wedge; (d) hardware slows sales cycles.
- **Why Leitmotif?** Squarely in the industrial AI thesis. Leitmotif and Eclipse are both investors in Redwood Materials (co-investor relationship). Volkswagen Group angle: production planning and inbound logistics at component plants is a workflow match in principle, but Noetive has no automotive evidence. Keep it as a hypothesis.

## 5. Ranked unknowns (by how much the answer moves the view)

1. **Product vs per-site engineering at Steuben** (systems read and written, sign-off, engineer-days, paid or not). → Call question 1.
2. **Whether "self-improving" transfers across customers** (what partner two reused from Steuben). → Call question 2.
3. **Role of the sensing pod in the value** (what it measures, how much gain remains without it, how many are installed). → Call question 3.
4. **Eclipse dependency and governance:** the CEO still holds the Eclipse Chief AI Officer title; Eclipse incubated the company and led the round. Round terms, board composition, Eclipse's pro-rata intentions and room for an outside Series A lead. → "What needs validation".
5. **Vertical focus:** which of manufacturing, logistics, energy, data centers and construction is the wedge for the next 12 months. → "What needs validation" (cut for space) and a fallback call question.
6. Model architecture (trained model vs frontier-LLM agents) and data rights for cross-customer learning.
7. Revenue (PitchBook says "Generating Revenue"), pricing model and team size.
8. HQ (Los Altos vs San Francisco) and whether any R&D sits in Israel (several angels are Israeli founders; unconfirmed).

## 6. Fallback call questions (if time allows)

- "Of manufacturing, logistics, energy, data centers and construction, which will you say no to for the next 12 months?"
- "Is your Eclipse Chief AI Officer role ending, and what did Eclipse get in the seed beyond its check (founder shares, board seats, pro-rata)?"
- "Is the brain a model you train, or orchestration over frontier models, and who owns what is learned from a customer's data?"

## 7. Material cut from the one-pager

- Construction pitched as a core vertical with no construction customer disclosed (Complete AI Training).
- Website use cases (per a search snippet): factory production planning, pallet and truck consolidation in logistics, construction schedule vs site conditions.
- The angel list in full (see register #6), including the three Decart co-founders, Yaser Sheikh and Boris Sofman.
- Eclipse's $1.3B April 2026 raise and its "back and build" model (Bedrock Robotics and Mind Robotics as earlier builds).
- Palantir Warp Speed (Anduril, L3Harris, Panasonic Energy, Shield AI) and the aerospace engine-output claim from Palantir's Q1 2026 call.
- Kinaxis named a Leader in the 2026 Gartner MQ for supply chain planning.
- Menachem Katz's title conflict (CEO vs co-CEO vs Henry Schwartz as CEO).

## 8. Next diligence steps

- Open noetive.ai, the PR Newswire release and the full SiliconANGLE and Calcalist articles from an environment with web access; confirm use cases and any metrics.
- Request a Steuben reference call (planning lead, not only the executive).
- Check Delaware or California registry records for Noetive AI Inc. (incorporation date, registered address).
- Pull LinkedIn headcount and team backgrounds, looking for industrial operators and hardware engineers.

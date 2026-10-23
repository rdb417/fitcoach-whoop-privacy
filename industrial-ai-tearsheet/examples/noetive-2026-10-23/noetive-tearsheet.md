# Noetive

**Leitmotif · Pre-call tear sheet · Partner briefing**  
Intro call with founders · Week of 2026-10-26

> AI agents plus in-house floor sensors that take over operational decisions such as production planning in plants and logistics; Eclipse-built, one named customer, $41M seed [1,2].

| Website | Headquarters | Founded | Stage | Capital raised |
|---|---|---|---|---|
| noetive.ai | Los Altos, CA [1] (press says San Francisco) | 2026 [1] | Seed | $41M seed, Sep 2026 [1] |

> **Read first.** Five-month-old company built inside its lead investor, Eclipse; the CEO is still listed as Eclipse's Chief AI Officer [1,4]. noetive.ai and most articles could not be opened, so product detail rests on PitchBook and launch-coverage excerpts.

## A. Company and product
Agents run on top of a customer's existing systems and take over operational decisions, fed by a multimodal sensing pod Noetive designs: an "intelligence of record" [2] *(CR)*. Targets: manufacturing, logistics, energy, data centers [2].

## B. Technology and differentiation
A core model (the "brain") learns how one operation runs from system data and pod signals; each deployment is meant to improve the shared model [2] *(CR)*.

- **Not disclosed:** whether the brain is a trained model or agents on frontier LLMs, what the pod senses, how many pods are installed *(Unknown)*.
- **Integration:** reads Steuben's system data plus floor conditions [2]; whether agents write plans back to ERP or only advise is not disclosed *(Unknown)*.
- **Likely moat, if any:** operating data (plans, outcomes, floor signals) compounding across sites, plus planner reliance; not the model *(INF)*. Own pods add data rivals lack but slow rollout versus software on existing cameras.

## C. Market and competition
Wedge: production planning in food and beverage plants, today mostly ERP plus spreadsheets.

- **Palantir AIP:** production scheduling over ERP, MES and PLM data [6]; the default operational layer.
- **Kinaxis:** Maestro planning suite adding agents [7]; heavy for mid-size plants.
- **Archetype AI:** sensor-data foundation model, $35M Series A Nov 2025 [5]; closest on sensing.

## D. Team and financing
CEO Amir Frenkel: about a decade as Meta VP (GenAI, XR), earlier Google and Amazon [1,3]; Eclipse's Chief AI Officer since April 2026, and Noetive formed inside Eclipse [2]. CPO Dan Barak founded Stackbit (sold to Netlify) after Lyft and Meta [3]. Eclipse led, with eight funds and 11 angels (Bosworth, Al-Dahle, Schroepfer) [1]. No founder with plant operations experience disclosed *(Unknown)*.

## E. Commercial traction
Sole named customer Steuben Foods (aseptic contract manufacturer): its executive Menachem Katz says planning that ran monthly over a week now runs daily in minutes [2]. Design partnership; paid status, vendor effort unknown *(Unknown)*. PitchBook lists revenue, no figures [1].

## F. Preliminary investment perspective
**What is interesting.** A customer-quoted week-to-minutes planning gain [2] is a concrete signal at five months. Interesting if it holds without Noetive engineers and transfers to a second plant *(INF)*.

**What needs validation.** Product versus per-site engineering; and Eclipse dependency (it built the company and employs the CEO [1,2]): check terms, board and room for an outside Series A lead.

**Leitmotif relevance.** Fits the industrial AI focus. Planning and inbound logistics at Volkswagen Group component plants could match once results extend beyond food *(INF)*. No portfolio overlap found.

## G. Three questions for the introductory call
1. **At Steuben, which systems do you read and write, who signs off the daily plan, and how many of your engineer-days did it take?** *Separates product from forward-deployed services.*
2. **What did your second design partner reuse from the Steuben model, and what was rebuilt?** *Tests self-improvement.*
3. **What does the pod capture at Steuben that ERP data missed, and how much gain remains without it?** *Moat or drag?*

---

*Evidence tags: (CR) company-reported, not independently verified · (INF) analyst inference · (Unknown) not established · [n] cites the source list.*  
*Research date 2026-10-23 · Independent research: PitchBook and web search; company site and most articles could not be opened*

**Sources**

1. PitchBook, Noetive profile, deals, team, investors (accessed 2026-10-23) <https://my.pitchbook.com/profile/1497563-29/company/profile>
2. SiliconANGLE, Noetive launches with $41M (via PitchBook excerpt) (2026-09-16) <https://siliconangle.com/2026/09/16/noetive-launches-with-41m-to-bring-self-improving-ai-to-factories-and-logistics/>
3. Craft Ventures, Our partnership with Noetive (via PitchBook excerpt) (2026-10-06) <https://www.craftventures.com/articles/our-partnership-with-noetive-building-the-intelligence-of-record-for-the-physical-economy>
4. Eclipse, Team page, Amir Frenkel (search snippet) (accessed 2026-10-23) <https://eclipse.capital/team/amir-frenkel>
5. Business Wire, Archetype AI raises $35M (search snippet) (2025-11-20) <https://www.businesswire.com/news/home/20251120000333/en/>
6. SoftwareOne, Palantir AIP for Production Scheduling (snippet) (accessed 2026-10-23) <https://platform.softwareone.com/product/aip-for-production-scheduling-management/PCP-3409-0127>
7. Kinaxis, 2026 Gartner MQ release (search snippet) (2026) <https://investors.kinaxis.com/news-releases/news-release-details/2026/Kinaxis-Recognized-as-a-Leader-in-the-2026-Gartner-Magic-Quadrant-Reports-for-Supply-Chain-Planning/default.aspx>

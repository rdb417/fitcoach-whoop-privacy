# Industrial AI Assessment Framework

Use this to decide which industrial factors matter for *this* company and to probe them. Do not score every dimension: pick the three or four that most determine whether the business can scale, and say little or nothing about the rest.

## Contents
1. The seven deployment dimensions
2. The maturity ladder: demo to repeatable production
3. Customer economics: where industrial value comes from
4. Archetype lenses
   - 4a. Computer vision inspection and quality
   - 4b. Robotics foundation models and embodied AI
   - 4c. Process optimization and industrial analytics
   - 4d. Autonomous manufacturing and factory automation
   - 4e. Predictive maintenance and asset monitoring
   - 4f. Industrial copilots, agents and engineering software
   - 4g. Simulation, digital twins and synthetic data
5. Separating real differentiation from "proprietary AI"
6. Incumbents and alternatives checklist

---

## 1. The seven deployment dimensions

| Dimension | Questions | What a strong answer looks like |
|---|---|---|
| **Workflow** | Which operational task is automated, optimized or augmented? Who did it before, and how? | A named task with a measurable output (e.g., "final visual inspection of machined housings, currently 3 inspectors per shift") |
| **Customer environment** | What factory type, process, asset class, or operating environment is required? Discrete vs process vs hybrid? Greenfield vs brownfield? | Clear boundaries on where it works and where it does not |
| **Integration** | Does it need PLC, SCADA, DCS, MES, ERP, historian (e.g., AVEVA PI), robot controller, or new sensors? Read-only or closed-loop write-back? | Standard interfaces (OPC UA, MQTT, Modbus, vendor robot SDKs) and a short list of supported systems |
| **Operational robustness** | Reliability, safety, latency, uptime, lighting, dust, vibration, temperature, part variation, network constraints | Quantified performance in production conditions, not lab conditions |
| **Deployment burden** | Configuration, data collection, labeling, retraining, custom engineering, on-site time per deployment | Engineer-days per new line or site, trending down across customers |
| **Scalability** | Can it move across lines, sites, product variants, and verticals without re-engineering? | Second and third sites at the same customer deployed faster and with less vendor involvement |
| **Human involvement** | Assistive, supervised, partially autonomous, or fully autonomous? Who is accountable for decisions? | The autonomy level matches what customers will actually sign off on today |

Closed-loop control (the AI writes setpoints or commands to equipment) is a much higher bar than advisory output. It raises safety, liability, cybersecurity (IEC 62443) and change-management requirements, and lengthens sales cycles. Note which side of that line the company is on.

Safety standards worth recognizing when robots or machines are involved: ISO 10218 (industrial robots), ISO/TS 15066 (collaborative operation), IEC 61508 / ISO 13849 (functional safety), and the EU Machinery Regulation (applies from 2027). Mention only when relevant.

## 2. The maturity ladder: demo to repeatable production

Place the company on this ladder using evidence, and say which rung each claim supports. These are not interchangeable.

1. **Concept / lab demo**: works on the team's own data or rig.
2. **Customer-data demo / unpaid POC**: works on customer data, often offline.
3. **Paid pilot**: customer pays, usually one line or cell, often with heavy vendor support.
4. **Production deployment**: runs in daily operations, customer relies on output.
5. **Repeatable production**: multiple sites or customers, deployment time falling, customer staff operate it.
6. **Platform expansion**: new use cases sold into the installed base.

Common gaps between rungs: pilot purgatory (rung 3 for 12+ months), a "production" system that still has a vendor engineer on site, and a "deployment" that is one robot cell in a corner of the plant. An announced partnership with an OEM or incumbent is not a rung at all until it names a deployed use case.

## 3. Customer economics: where industrial value comes from

Tie the value case to a specific line item. Typical drivers:

| Driver | Typical metric | Sanity check |
|---|---|---|
| Labor productivity | FTEs per shift, hours per unit | Is labor actually removed or redeployed? Labor scarcity often matters more than cost |
| Equipment utilization | OEE, availability | OEE gains are often claimed against an unclear baseline |
| Scrap and rework | Scrap rate, first-pass yield | Value per point of scrap varies hugely by material cost |
| Yield | Good units per input | Most powerful in high-value processes (semiconductors, batteries, pharma, specialty chemicals) |
| Throughput | Units per hour, cycle time | Only valuable if the line is capacity constrained |
| Downtime | Unplanned downtime hours | Ask for avoided events, not "predicted failures" |
| Energy and materials | kWh or feedstock per unit | Strong in process industries and energy-intensive plants |
| Capital avoidance | Deferred line or plant investment | Rare but very large; requires credible capacity uplift |
| Quality escapes | Warranty cost, recalls, customer claims | High value but hard to attribute |

When a company claims ROI or payback, check: Is the baseline stated? Is it one site or an average? Does it net out the vendor's fees and the customer's internal effort? Is it customer-confirmed? If not, it is `{CR}`.

## 4. Archetype lenses

Most companies fit one primary lens, sometimes two. Use the lens to know where to dig.

### 4a. Computer vision inspection and quality

- **How it works**: cameras (2D, 3D, hyperspectral, X-ray, thermal) plus models for defect detection, classification, measurement; often edge inference at the station.
- **Where differentiation can live**: data efficiency (few-shot onboarding of new variants), hard modalities (3D, X-ray, specular or transparent surfaces), defect taxonomies for a specific process, closed-loop root cause linking defects to process data, or integration depth with MES/traceability.
- **Where it usually does not**: the detection model itself; strong open models and incumbent deep-learning tools make generic defect detection a commodity.
- **Deployment burden signals**: labeled images needed per new part, retraining frequency, lighting and fixturing work, false-reject tolerance at line speed.
- **Red flags**: accuracy quoted without false-reject rate; "99%" with no defect base rate; single-customer data.
- **Alternatives**: Cognex, Keyence, Zeiss, Omron, Basler-based integrator builds, in-house vision teams at large manufacturers, other AI-native vision startups (check current players for the specific vertical).

### 4b. Robotics foundation models and embodied AI

- **How it works**: large models (often vision-language-action, VLA) that map perception and instructions to robot actions; trained with teleoperation data, imitation learning, reinforcement learning, simulation, and internet-scale video or text priors.
- **Where differentiation can live**: proprietary real-world robot data at scale (and the flywheel that produces it), cross-embodiment generalization, data collection efficiency, sim-to-real transfer, real-time inference on robot hardware, and a credible path to a business model (model licensing, full-stack robots, or vertical applications).
- **What to separate**: research progress (benchmarks, demo videos) from deployed task success rates, intervention rates, and cycle time against human or classical automation.
- **Deployment burden signals**: task-specific data needed per new deployment, teleop hours per task, safety case for working near people.
- **Red flags**: demos with hidden teleoperation or heavy cuts; no stated success rate; capital needs far beyond the round without a clear financing path; unclear owner of the hardware.
- **Alternatives**: other foundation-model labs (check current: e.g., Physical Intelligence, Skild AI, Google DeepMind robotics, NVIDIA's GR00T ecosystem), humanoid full-stack players, and plain classical automation, which often wins on cost and reliability for structured tasks.

### 4c. Process optimization and industrial analytics

- **How it works**: models over historian and sensor data (soft sensors, surrogate models, multivariate optimization, reinforcement learning, sometimes hybrid physics/ML) that recommend or set process parameters.
- **Where differentiation can live**: handling sparse, noisy, drifting plant data; explainability that process engineers accept; closed-loop control with safety guardrails; vertical templates that cut time-to-value (e.g., cement, chemicals, steel, batteries, food).
- **Deployment burden signals**: data engineering per site, historian access, the role of the customer's process engineers, time to first recommendation.
- **Red flags**: "AI" that is mostly consulting; value claims without a controlled comparison; no answer to model drift.
- **Alternatives**: APC/optimization suites from AspenTech, AVEVA, Honeywell, Emerson, Siemens, Rockwell, Yokogawa; analytics tools like Seeq; in-house data science teams; established AI-native players in the vertical (check current).

### 4d. Autonomous manufacturing and factory automation

- **How it works**: software-defined production cells or factories combining robots, sensors, planning software and AI for tasks like machining, assembly, forming, welding or kitting; sometimes the startup operates its own factory and sells parts, not software.
- **Where differentiation can live**: automating high-mix, low-volume work that classical automation cannot justify; software that removes per-part programming; process know-how in a hard manufacturing step.
- **Key business-model question**: Are they a technology vendor (sell cells or software), a robots-as-a-service provider, or a manufacturer (sell parts)? Margins, capital intensity and valuation logic differ completely.
- **Deployment burden signals**: integration time per cell, programming time per new part, reliance on system integrators.
- **Red flags**: capital intensity without margin evidence; contract-manufacturing economics presented as software economics.
- **Alternatives**: system integrators with Fanuc, ABB, KUKA, Yaskawa robots; Siemens and Rockwell automation stacks; contract manufacturers; other AI-native automation startups in the same process (check current).

### 4e. Predictive maintenance and asset monitoring

- **How it works**: vibration, acoustic, thermal, electrical or process signals with anomaly detection and failure prediction; often proprietary sensors plus software.
- **Differentiation**: failure-mode libraries across many assets, sensor economics, low false-alarm rates, actionable diagnoses rather than alerts.
- **Red flags**: "predicted failures" without avoided-downtime evidence; alert fatigue at customers; hardware margins hidden in a SaaS story.
- **Alternatives**: Augury, Siemens, ABB, SKF, GE Vernova, Honeywell, AVEVA, plus maintenance teams' existing condition-monitoring vendors.

### 4f. Industrial copilots, agents and engineering software

- **How it works**: LLM-based systems over manuals, work instructions, maintenance logs, CAD/PLM, PLC code or MES data; agents that draft PLC logic, troubleshoot equipment, generate work instructions, or answer operator questions.
- **Differentiation**: structured access to proprietary industrial data, domain-specific evaluation and guardrails, write access to engineering tools, and workflow embedding. Model choice alone is not a moat.
- **Red flags**: a chat interface over PDFs with no workflow ownership; no accuracy evaluation; incumbents (Siemens Industrial Copilot and similar) bundling the same capability.
- **Alternatives**: incumbent copilots from automation and PLM vendors, Microsoft and other platform tools, internal IT builds.

### 4g. Simulation, digital twins and synthetic data

- **How it works**: physics or neural simulators, scene reconstruction, synthetic data for training perception or robot policies, plant-level twins for planning.
- **Differentiation**: sim-to-real fidelity proven on customer outcomes, speed, and ownership of the asset models.
- **Red flags**: twins that are visualizations; no measured downstream benefit.
- **Alternatives**: NVIDIA Omniverse/Isaac ecosystem, Siemens (Process Simulate, Tecnomatix), Dassault Systèmes, Ansys (Synopsys), in-house simulation teams.

## 5. Separating real differentiation from "proprietary AI"

Ask, in order:
1. **Is the model the product?** If the core model is fine-tuned from an open or commercial model, the moat must come from somewhere else.
2. **Data**: Do they have data others cannot easily get (labeled defects across many plants, robot interaction data, process data with outcomes)? Is there a mechanism that compounds it with each deployment?
3. **Integration and workflow**: Do they own a hard integration (robot controller, closed-loop control, MES write-back) or a workflow that customers will not rip out?
4. **Hardware or sensing**: Is there a sensor, end-effector, or cell design that enables the AI?
5. **Process know-how**: Do they understand a manufacturing process well enough to know what to measure and control?
6. **Speed of deployment**: Is time-to-value structurally lower than alternatives, and is it measured?

Write the answer as a plain statement of the most plausible moat, tagged `{INF}`, and what would disprove it.

## 6. Incumbents and alternatives checklist

For the competition section, cover two to four of the most relevant from these categories, not a long list:
- The incumbent product line a plant would default to.
- The system integrator or in-house build path.
- One or two venture-backed direct competitors attacking the same workflow.
- The "do nothing" baseline (manual inspection, existing PM schedule, classical automation).

Before naming a competitor, confirm it exists, is still independent and operating, and actually targets the same workflow. Startups in robotics and AI get acquired, license their technology away, or pivot often.

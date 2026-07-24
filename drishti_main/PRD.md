# Drishti — PRD
KSP x Hack2skill Datathon 2026, Challenge 2. Prototype deadline: Sun Jul 26 2026, 11:59 PM IST.

## Problem
KSP/SCRB manages 1100+ police station records via fragmented, Excel-heavy processes. No advanced analytics, no cross-station visibility, policing stays reactive instead of proactive.

## What we're building
Drishti — a two-tier crime intelligence platform on Zoho Catalyst (mandatory deployment target):
- **Station Console** — operational view for a single station
- **Command Console** — SCRB-level oversight: hotspot map, resolution accountability, network analysis

## Core features (must-have — the actual gate for shortlisting)
1. **Geospatial hotspot map** — district drill-down, DBSCAN-based statistical clustering (not just visual pin-grouping), choropleth by crime volume
2. **Anomaly / trend-spike detection** — flags stations/crime-heads deviating from historical baseline, the brief's "Emerging Trend Alerts" — added after an audit caught it missing, treat as must-have, not stretch
3. **Resolution feedback loop** — per-station resolution rate (Chargesheeted / False Case / Undetected), tracked over time — this is the accountability differentiator
4. **Network/link analysis** — graph view connecting Accused ↔ Victim ↔ shared cases, surfaces repeat offenders

## Stretch features (only if ahead of schedule — see kill order in TEAM_MASTER_PLAN.md)
- Predictive risk score (simple weighted formula, not a real ML claim, unless time allows a real one)
- 3-tier RBAC (Station → PI → DySP/ACP), degrade to flat 2-tier if short on time

## Why this wins (the differentiator, not just a checklist)
Existing systems (CCTNS, M-CCTNS, G-CARE) are record-keeping tools. Drishti closes the loop: not just "what happened" but "was it resolved, by whom, and how does this station compare to others." Judging research indicates deployability + a genuinely working system is weighted heavily — a working Catalyst deployment beats a fancier local prototype.

## Data
Official Karnataka Police FIR ER Diagram (source of truth schema) + synthetic incident CSV, reshaped to match the normalized schema. See `drishti_catalyst_schema.md` for full table definitions.

## Non-negotiables
- Must deploy on Zoho Catalyst (AppSail + Data Store + Slate) — third-party alternatives risk submission validity
- PII fields (names, KGID, DOB) flagged with Catalyst's PII validator
- Caste/Religion data stays in schema/backend but is NOT a standalone chart in the demo UI — fold into broader socio-economic overlay only

## Success criteria for this deadline (Jul 26, 11:59 PM IST)
A live, Catalyst-hosted URL where a judge can: view the map with real clustered incidents, drill into a district/station, see resolution metrics for at least 2–3 stations, and see at least one working network graph example. Everything else is bonus.

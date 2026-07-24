# Drishti — Complete Solution Blueprint
KSP x Hack2skill Datathon 2026, Challenge 2. Prototype deadline: Sun Jul 26 2026, 11:59 PM IST.
This is the single-file, no-division view — use it to check nothing has fallen through the cracks.

---

## 1. What we're building and why it stands up

**Problem:** KSP/SCRB manages 1100+ station records via fragmented, Excel-heavy processes. No advanced analytics, no cross-station visibility, policing stays reactive.

**Solution:** Drishti — a two-tier crime intelligence platform on Zoho Catalyst. Station Console (operational) + Command Console (SCRB-level oversight): hotspot map, resolution accountability, network analysis, anomaly alerts.

**Why it stands up, specifically:**
- **Deployability is the actual gate.** Research into KSP's judging structure found deployability and a genuinely working system weighted heavily over polish — the funnel is idea → prototype → prototype evaluation (a hard gate) → demo. A working Catalyst deployment beats a fancier local prototype. We front-loaded the Catalyst risk (Block 0) instead of treating it as a deployment afterthought.
- **The differentiators are grounded in the real official ERD, not invented.** Resolution loop, network analysis, and anomaly detection all fall out of tables that already exist in the Karnataka Police FIR schema (`CaseStatusMaster`, `ChargesheetDetails`, `Accused`/`Victim`) — this isn't scope invented to sound impressive, it's the actual schema doing real work.
- **Prior-year reference repos found in research (CopSight, KSP-Dashboard-Datathon) were flat KPI dashboards.** Nobody found combined link analysis + resolution accountability + anomaly detection in one system — that combination is still the real differentiator.

---

## 2. Brief requirement → build status (the actual audit)

| Brief capability | Status | Where it lives |
|---|---|---|
| District-level drill-down | ✅ Built | Command Console, map |
| Spatiotemporal clusters ("Crime Hotspots") | ✅ Built | DBSCAN clustering → `HotspotCluster` → `/hotspots` → map overlay |
| Emerging trend alerts / anomaly detection | ✅ Built (added late — was missing until this audit) | Historical-baseline deviation → `AnomalyFlag` → `/anomalies` → map/console callout |
| Relationship mapping (node-based) | ✅ Built | Accused/Victim/CaseMaster joins → network graph |
| Repeat offender tracking | ✅ Built | Same logic as above, by AccusedName/PersonID |
| Association detection | ✅ Built | Same network graph |
| MO (modus operandi) matching across jurisdictions | ⚠️ Partial | Implied by shared crime sub-head + repeat accused, not a dedicated MO-similarity feature — acceptable simplification for this deadline, real limitation to be upfront about if asked |
| Socio-economic correlation overlay | ❌ Deliberately deferred | No external demographic dataset reshaped in time; explicitly slotted for the Refined Prototype Submission Phase (Aug 19–30) — say this directly if asked, don't pretend it's built |
| Predictive risk scoring | ⚠️ Stretch only | Simple weighted formula if time allows (Block 5/kill-list #1) — do not call this "ML" unless a real model is actually behind it |
| Resolution feedback loop (not explicitly in brief, our own differentiator) | ✅ Built | `CaseStatusMaster` + `ChargesheetDetails.cstype` → per-station resolution rate |
| Cross-station accountability (our own differentiator) | ✅ Built | Grouping by `Unit`/`District` |

Two rows worth being honest about in the demo, not hiding: MO-matching is simplified, and socio-economic overlay is a stated roadmap item, not shipped. Both are legitimate, defensible scope calls given the deadline — being upfront about them is safer than a judge finding the gap themselves.

---

## 3. Architecture (unchanged from earlier, restated for completeness)

| Layer | Tech | Catalyst Service |
|---|---|---|
| Frontend | React + Tailwind + Leaflet + Recharts | Slate |
| Backend | FastAPI | AppSail (Python managed runtime) |
| Structured data | Full ERD-based schema | Data Store |
| Precomputed outputs | Hotspot clusters, anomaly flags | Data Store (small enough, queryable) |
| Auth | 2-tier (Station/Command), 3-tier stretch | Catalyst Authentication |
| Predictive risk (stretch only) | Simple formula or Zia AutoML | Zia AutoML / QuickML |
| Agent tooling | Catalyst-aware coding | `catalystbyzoho/agent-skills` (Gemini CLI extension) + Zoho MCP |

Full column-level schema: `drishti_catalyst_schema.md`. Catalyst technical constraints (cold start, read-only FS, C-extension mismatch, 30s timeout, request-bound SDK, no DDL via SDK): `drishti_architecture.md`.

---

## 4. Complete phase list (content view, not who-does-it)

**Phase 0 — De-risk:** AppSail hello-world survives cold start with heavy imports lazy-loaded. Data Store round-trip confirmed live. Slate bare frontend deployed. Agent-skills extension installed, Zoho MCP table-creation capability tested.

**Phase 1 — Data foundation:** Schema created batch-by-batch (A→B→C→E) via console GUI. Synthetic CSV reshaped and normalized to match schema, district names reconciled against GeoJSON.

**Phase 2 — Backend core:** Incident CRUD, hotspot endpoint, anomaly endpoint, accused/victim endpoints, resolution endpoint, auth. Every endpoint deployed and verified live before the next one starts.

**Phase 3 — Frontend core:** Map (raw pins + choropleth), Station Console, Command Console shells — built against mock data in parallel with Phase 2, swapped to real endpoints as they ship.

**Phase 4 — Differentiators surfaced in UI:** Hotspot overlay (distinct from visual pin clustering), anomaly/trend-spike indicator, resolution-loop panel, network graph.

**Phase 5 — Stretch, only if ahead:** Predictive risk score, 3-tier RBAC.

**Phase 6 — Integration + bug bash:** Full flow tested end-to-end (login → console → map → hotspots/anomalies → resolution → network graph). Feature freeze. Fixes only.

**Phase 7 — Host + submit:** Production deploy to Zoho, verified against the live URL, demo materials prepared, submitted with buffer before 11:59 PM.

---

## 5. Non-negotiables

**Never cut:** Live Catalyst deployment end-to-end, the map (with real hotspot clustering, not just pins), the resolution loop.

**Kill list if behind schedule, in order:** predictive risk score → 3-tier RBAC (degrade to flat 2-tier) → network graph depth (fewer node types, keep concept) → lookup table completeness (3–4 seed rows for low-priority tables). Anomaly detection and hotspot clustering are NOT on the kill list — they were the actual gap this audit caught, don't let them silently drop a second time.

**PII/optics:** PII validator enabled on name/ID/DOB fields. Caste/Religion never surfaced as a standalone chart, folded into broader socio-economic framing only — and that broader framing itself is deferred per the audit above, so for this deadline, caste/religion data effectively stays backend-only.

---

## 6. What to say if a judge asks about a gap
"Socio-economic correlation and full MO-pattern matching are scoped for the Refined Prototype phase (Aug 19–30) — we prioritized deployability and the three core differentiators [hotspot detection, resolution accountability, network analysis] for this gate, since a working, evaluable system was the stated priority." This is a true, confident answer, not an excuse.

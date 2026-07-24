# Drishti — Architecture (Reference)
KSP x Hack2skill Datathon 2026, Challenge 2. Prototype deadline: Sun Jul 26 2026, 11:59 PM IST.

## Problem statement (condensed)
KSP/SCRB manages 1100+ station records via fragmented, Excel-heavy processes. No advanced analytics, no cross-station visibility, policing stays reactive. Brief asks for three capability pillars:
1. Advanced visualization — district drill-down, spatiotemporal hotspots, trend-spike alerts
2. Network/link analysis — suspect-victim-location graphs, repeat-offender MO tracking across jurisdictions
3. Sociological/predictive intelligence — socio-economic overlays, predictive risk scoring, anomaly detection

## Solution: Drishti
Two-tier (station / command) crime intelligence platform on Catalyst. Core precomputed analytics (no live inference in request path). Three differentiators chosen deliberately because the official ERD already supports them with near-zero extra schema:
- **Resolution feedback loop** — falls out of `CaseStatusMaster` + `ChargesheetDetails.cstype`
- **Network/link analysis** — falls out of `Accused`/`Victim` linked via `CaseMasterID`, computed on demand
- **Cross-station accountability** — falls out of grouping by `Unit`/`District`

## Stack → Catalyst service mapping
| Layer | Tech | Catalyst Service |
|---|---|---|
| Frontend | React + Tailwind + Leaflet + Recharts | Slate (Web Client Hosting) |
| Backend | FastAPI (Python managed runtime) | AppSail |
| Structured data | Incident/case/org records | Data Store (schema in `drishti_catalyst_schema.md`) |
| Precomputed outputs | Hotspot cluster JSON, anomaly flags, network graph edges | Stratus / Data Store (small enough for either) |
| Auth | Role-based, 2–3 tier | Catalyst Authentication |
| Predictive risk (optional, low priority) | Tabular model | Zia AutoML / QuickML |
| Routing | — | Catalyst API Gateway (in front of AppSail) |
| Agent tooling | Catalyst-aware coding agent | `catalystbyzoho/agent-skills` (install as Gemini CLI extension) + Zoho MCP |

## RBAC shape
Research indicates KSP rewards hierarchical rollup, not flat 2-tier: Station → PI (Police Inspector) aggregation → DySP/ACP aggregation. Build the 2-tier Station/Command split first (must-have); add the PI mid-tier only if time allows (nice-to-have, cut first under pressure).

## Catalyst technical constraints — confirmed from research, build around these from Block 0
- **10-second cold start**: app must bind to `X_ZOHO_CATALYST_LISTEN_PORT` within 10s of container spawn or AppSail kills it. Lazy-import heavy libs (pandas/sklearn/networkx) inside route handlers, not at module load.
- **Read-only filesystem**: no local SQLite/temp file writes. Use Catalyst Cache or Stratus for any intermediate output.
- **Native dependency mismatch**: packages with C-extensions built locally (Windows/Mac) won't run in AppSail's Linux container. Predeploy step required: `pip install --only-binary=:all: --platform manylinux2014_aarch64 -r requirements.txt -t .`
- **30-second request timeout**: any Zia AutoML/LLM call inside a route must finish in 30s or gets killed. Long inference → Job Scheduling/Cron, poll for result, don't block a request on it.
- **No WebSockets**: "live" alerts/updates need polling, not push.
- **No schema-as-code**: Data Store tables created manually via console GUI only; ZCQL is DML-only (SELECT/INSERT/UPDATE/DELETE), no CREATE/ALTER/DROP TABLE via SDK or API. Verify in Block 0 whether Zoho MCP's "create tables" claim is a genuine exception (separate admin API) or requires the same manual step.
- **SDK is request-bound**: `zcatalyst-sdk` must be initialized per-request with the request object, not globally at startup — write this as FastAPI middleware/dependency, don't fight it with global client patterns.
- **Concurrency ceiling**: 100 req/instance, 5 instances max, 500 global concurrency, 5-minute instance lifespan (recurring cold starts). Unlikely to matter for a hackathon demo, but don't design around long-lived connections.

## PII / optics handling
Enable Catalyst's PII/ePHI validator on: `ComplainantName`, `VictimName`, `AccusedName`, `Employee.KGID`, `Employee.FirstName`, `Employee.EmployeeDOB`. `CasteMaster`/`ReligionMaster` stay in schema and backend (legitimate per brief) but do not surface as a standalone "crime by caste/religion" chart in the demo UI — fold into a broader socio-economic overlay (occupation, urbanization) instead.

## Full Data Store schema
See `drishti_catalyst_schema.md` — batch build order (A: lookups → B: org/people → C: core case → D: lifecycle → E: Drishti analytics extension), full column/type/key tables, PII flags, and the two documented ambiguities in the source ERD (`Inv_OccuranceTime`, `inv_arrestsurrenderaccused`) with defaults already chosen.

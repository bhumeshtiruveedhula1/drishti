# Drishti — Gamma TRD (Data Layer + Analytics Logic + Demo Prep)
Read `PRD.md` and `TEAM_MASTER_PLAN.md` first. This is your task-level detail. Your tasks are more self-contained on purpose — you're not blocked by anyone at the start, and your output unblocks Alpha and Beta.

## Your ownership
Reshaping synthetic data to match the real schema, seeding lookup tables, the network/link-analysis join logic, data quality, and the demo storyline. This work matters as much as the code — bad or obviously-fake-looking data undercuts everything Alpha and Beta build.

## Hour 0 tasks
1. Clone the repo, checkout `gamma/data-analytics`.
2. Open the flat synthetic CSV and `drishti_catalyst_schema.md` side by side.
3. Fix district name mismatches between the CSV and the Karnataka GeoJSON now (old spellings like "Bangalore" vs "Bengaluru") — this is the single most important early task, a silent mismatch here breaks the map later with no error message.
4. Reshape the flat CSV into separate seed files per table for Batch A (State, District, UnitType, CaseCategory, GravityOffence, CrimeHead, CrimeSubHead, CaseStatusMaster, CasteMaster, ReligionMaster, OccupationMaster, Act, Section).

## Antigravity prompt — Hour 0 task
```
CONTEXT: Block 0/1, data reshaping
TASK: Given the flat synthetic_incidents.csv and the table definitions in drishti_catalyst_schema.md
(Batch A lookup tables), write a Python script that:
1. Extracts unique values for each lookup table (districts, crime categories, crime heads, etc.)
2. Assigns sequential IDs matching each table's PK
3. Outputs one CSV per table, columns matching the schema exactly (same names, same order)
CONSTRAINTS: Cross-check district names against the Karnataka GeoJSON file's naming convention —
flag any name in the CSV that doesn't have an exact match in the GeoJSON, don't silently proceed.
DEFINITION OF DONE: Show me the list of any district name mismatches found, plus the output CSV
files' row counts per table.
DO NOT: touch Batch B/C tables yet, lookup tables only for this task.
```

## Build order
1. Batch A seed CSVs (above) → hand to Alpha for bulk load
2. Batch B/C seed data (Unit/Employee/CaseMaster/Accused/Victim/ComplainantDetails) reshaped from the flat CSV, with correct FK IDs matching Batch A's assigned IDs
3. **DBSCAN hotspot clustering** (this is the actual analytical differentiator behind "the map" — not just visual marker grouping, don't skip this) — run DBSCAN on incident lat/lng per crime category/time window, output cluster centroids + incident counts matching the `HotspotCluster` table shape in the schema doc. Hand off as a JSON/CSV for Alpha to load or serve.
4. **Anomaly detection** — for each station/crime-head, compare current time-window incident count to a historical baseline (simple z-score or % deviation is fine). Flag anything crossing a threshold. Output matching the `AnomalyFlag` table shape in the schema doc. Reuses the same batch-script pattern as the hotspot task — do it right after.
5. Network/link-analysis join logic: given Accused/Victim/CaseMaster, find repeat offenders (same AccusedName or PersonID pattern across multiple CaseMasterIDs) and shared-location clusters — write this as a spec first, then as a draft endpoint for Alpha to review/merge
6. Recharts trend components (crime category over time, per-district volume) against mock data, handed to Beta
7. Demo storyline — pick 2–3 stations and 1–2 repeat-offender examples that will look clear and convincing on stage, verify the underlying data actually supports the story before the demo

## Antigravity prompt — DBSCAN hotspot clustering
```
CONTEXT: Block 1, hotspot detection (the real analytical map differentiator, not visual clustering)
TASK: Given the reshaped CaseMaster seed data (lat/lng, CrimeMajorHeadID, IncidentFromDate), run
DBSCAN clustering (scikit-learn) per crime category, tuning eps/min_samples so clusters reflect
genuine hotspots rather than noise. For each cluster, compute: centroid lat/lng, incident count,
crime head, time window. Output matching the HotspotCluster table columns in
drishti_catalyst_schema.md exactly.
CONSTRAINTS: Treat DBSCAN's -1 label as noise, exclude it from output clusters.
DEFINITION OF DONE: Show me the actual cluster output (at least 3-5 real clusters with centroid
and count) run against the real seed data, not a toy example.
DO NOT: build this as a live/on-request computation — it's a batch/offline script, per the
precomputation-only rule in the architecture doc.
```

## Antigravity prompt — link-analysis logic
```
CONTEXT: Block 1/4, network/link-analysis logic
TASK: Given the Accused, Victim, and CaseMaster tables (schema in drishti_catalyst_schema.md),
write a query/script that identifies:
1. Repeat offenders — same AccusedName appearing across multiple CaseMasterIDs
2. Shared-location clusters — multiple CaseMasterIDs with close lat/lng and overlapping Accused
Output as a small JSON graph structure: nodes (Accused/Victim/Unit) and edges (shared CaseMasterID),
scoped to a manageable subset (5-10 example offenders) for demo purposes, not the full dataset.
DEFINITION OF DONE: Show me the actual JSON output for at least 2 real example clusters found in
the seed data, not a hypothetical schema.
DO NOT: build a full precomputed table for this — keep it as an on-demand query per
architecture doc's guidance.
```

## Errors you will likely hit — and the fix
- **Bulk insert of your seed CSVs fails partway through** → Catalyst likely caps rows per API call. Tell Alpha to chunk the insert rather than sending the whole file at once.
- **Date fields rejected on insert** → Catalyst's DATE/DATETIME columns expect an exact format (`YYYY-MM-DD` / `YYYY-MM-DD HH:MM:SS`). Reformat before handing off, don't assume pandas' default string output matches.
- **FK references point to nothing** → if your Batch B/C seed data was generated before Batch A's IDs were finalized, the FK IDs won't line up. Always generate Batch A first, lock its ID assignments, then generate everything that references it.
- **Network graph output looks technically correct but empty/boring** → check whether the synthetic data actually has enough repeat-offender overlap; if not, this is worth flagging early rather than discovering it during demo prep on Day 2 with no time to fix it.
- **District names "fixed" in the CSV but the GeoJSON has yet another different spelling** → don't assume there's only one string to fix; check every district name against the actual GeoJSON properties field, not just the ones you remember seeing.

## Git checkpoints
Push to `gamma/data-analytics` continuously. Hand seed data files to Alpha as soon as each batch is ready — don't batch up all of it until the end, that creates a bottleneck for Alpha right when time gets tight.

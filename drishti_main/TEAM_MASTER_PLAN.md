# Drishti — Team Master Plan
Start: Tomorrow, 8:00 AM. Deadline: Sun Jul 26 2026, 11:59 PM IST. Read this fully before anyone starts.

## Roles (functional split, not a hierarchy)
- **Alpha** — Catalyst infra + backend. Highest-risk, sequential path everything else depends on. Starts first, nothing waits on anyone else to begin.
- **Beta** — Frontend: map, consoles, graph visualization. Builds against mocked data first, swaps to real endpoints as Alpha ships them.
- **Gamma** — Data layer + analytics logic + demo prep. Reshapes synthetic data, seeds lookup tables, builds the network/link-analysis query logic, owns the demo storyline and QA.

Nobody waits idle. If your task is blocked, move to the next task listed for you, don't sit on a dependency.

## GitHub setup (Alpha does this first, hour 0)
Repo: single repo, e.g. `drishti-datathon`. Branches:
- `main` — protected, only merged into right before final production deploy
- `dev` — integration branch, everyone merges here at checkpoints, tested before touching `main`
- `alpha/backend` — Alpha's working branch
- `beta/frontend` — Beta's working branch
- `gamma/data-analytics` — Gamma's working branch

Commit convention: `[alpha] `, `[beta] `, `[gamma] ` prefix on every commit so history stays readable across three people. Push continuously to your own branch — don't hoard uncommitted work.

**Merge checkpoints into `dev`:** end of Day 1 evening, mid Day 2, end of Day 2 evening. Whoever merges last at each checkpoint resolves conflicts before moving on — don't let conflict resolution slide to the next checkpoint.

**Merge to `main`:** only on Day 3 morning, after full integration testing on `dev`, right before the final Zoho production deploy.

## Schedule (hour blocks — map to actual clock times starting tomorrow 8 AM)

### Day 1, 8:00–12:00 — De-risk + parallel scaffolding
- **Alpha:** Create repo, share access. Deploy trivial FastAPI hello-world to AppSail, confirm it survives cold start with pandas/sklearn imported. Manually create 2–3 Data Store tables via console, confirm SDK read/write round-trip from the *deployed* app.
- **Beta:** Scaffold React + Tailwind + Leaflet locally, mock JSON matching the schema shapes, push initial commit. Get a bare map rendering with fake pins.
- **Gamma:** Reshape the flat synthetic CSV into per-table seed data matching Batches A/B/C in the schema (State, District, CrimeHead, CrimeSubHead, CaseCategory, GravityOffence, CaseStatusMaster, etc.). Fix district name mismatches (GeoJSON vs CSV) now.

### Day 1, 12:00–18:00 — Core build, first integration point
- **Alpha:** Click-create remaining Batch A/B/C tables. Build CaseMaster + Accused + Victim CRUD endpoints. Deploy and verify each live as built.
- **Beta:** Build Station Console + Command Console layouts against mock data. Push to `beta/frontend`.
- **Gamma:** Hand Alpha the seed data (CSV/JSON per table) for bulk load. Run DBSCAN hotspot clustering against the reshaped incident data — this is the real analytical map differentiator, not optional. Start building Recharts trend components against mock data.

### Day 1, 18:00–23:00
- **Alpha:** Finish core case CRUD, deploy, verify live. Expose `GET /hotspots` from Gamma's cluster output. Start resolution-loop aggregation endpoint (group by station/status).
- **Beta:** First mock-to-real swap — wire the map to Alpha's live incident endpoint. Continue console polish.
- **Gamma:** Run anomaly detection (historical-baseline deviation per station/crime-head) — reuses the hotspot script's data, do it right after. Draft the network/link-analysis join query (Accused/Victim/CaseMaster) as a spec or draft endpoint.

**Checkpoint (end of Day 1):** merge `alpha/backend` and `gamma/data-analytics` into `dev`. Confirm Beta's map swap works against real data on `dev`.

### Day 2, 8:00–14:00
- **Alpha:** Expose `GET /anomalies` from Gamma's output. Finish + deploy resolution-loop endpoint. Set up Catalyst Authentication for 2-tier roles. Stretch: risk score endpoint (simple formula) if ahead of schedule.
- **Beta:** Wire the hotspot overlay and anomaly indicator into the map (distinct from raw pins). Build resolution-loop UI (Command Console panel). Wire network graph component (`react-force-graph` or `vis-network`) to Gamma's endpoint.
- **Gamma:** Finalize the link-analysis endpoint (with Alpha reviewing/merging it). Support Alpha/Beta integration bugs. Start assembling the demo script — which flow gets shown, in what order.

### Day 2, 14:00–20:00 — Integration push
All three: merge everything into `dev`, run the full flow end-to-end (login → console → map → resolution panel → network graph). Fix what breaks. No new features from this point unless something planned is trivially incomplete.

### Day 2, 20:00–23:00
Continue bug fixing only. **Hard feature freeze at 23:00** — nothing new after this, regardless of how tempting.

### Day 3 (deadline day), 8:00–12:00 — Bug bash only
Fix only what's broken in the exact path you'll demo/submit. Merge `dev` → `main`.

### Day 3, 12:00–18:00 — Host + verify (the half-day buffer)
Deploy `main` to Zoho production. Verify the production URL end-to-end, not just the dev environment. Prepare demo video/writeup/submission materials.

### Day 3, 18:00–23:00 — Submit
Submit with buffer before 11:59 PM. Assume the submission portal itself will have some friction — don't do this at 11:55.

## Kill list if behind schedule (in order)
1. Predictive risk score
2. 3-tier RBAC → flat 2-tier
3. Network graph depth → fewer node types, keep the concept
4. Lookup table completeness → 3–4 seed rows each for lower-priority tables

Hotspot clustering and anomaly detection are NOT on this list — they're must-have per the PRD, don't deprioritize them under pressure.

## Never cut
Live Catalyst deployment, the map (with real hotspot clustering), the resolution loop.

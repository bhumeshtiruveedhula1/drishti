# Drishti — Alpha TRD (Catalyst Infra + Backend)
Read `PRD.md` and `TEAM_MASTER_PLAN.md` first. This is your task-level detail.

## Your ownership
AppSail deployment, Data Store schema creation, FastAPI backend, all live endpoints, Catalyst Authentication. You are the critical path — everyone else depends on your endpoints existing and being live.

## Hour 0 tasks
1. Create the GitHub repo, branches per `TEAM_MASTER_PLAN.md`, invite Beta and Gamma.
2. Claim the Zoho Catalyst credits (promotions link from the datathon resources page) — quick, don't skip it.
3. Install the `catalystbyzoho/agent-skills` Gemini CLI extension (`gemini extensions install https://github.com/catalystbyzoho/agent-skills`) before writing any Catalyst-specific code with Antigravity — this is what reduces the risk of it hallucining Data Store/AppSail SDK syntax. Test whether its Zoho MCP connection can actually create Data Store tables, or whether table creation stays manual-only despite the tooling — note the answer, it affects how much of Batch A/B/C you script vs click by hand.
4. In Catalyst console → Project-Rainfall → Serverless → AppSail → create app, Python managed runtime.
5. Deploy a bare FastAPI hello-world. Confirm it binds to the port and responds within the cold-start window.

## Antigravity prompt — Hour 0 task (use as-is)
```
CONTEXT: Block 0, Catalyst AppSail deployment
TASK: Create a minimal FastAPI app with a single GET / route returning {"status":"ok"}.
Include a predeploy step that installs dependencies with:
pip install --only-binary=:all: --platform manylinux2014_aarch64 -r requirements.txt -t .
Do NOT import pandas/sklearn/networkx at module level — this app has no heavy deps yet, keep it minimal.
Read the port from the environment variable Catalyst provides (X_ZOHO_CATALYST_LISTEN_PORT), not a hardcoded port.
DEFINITION OF DONE: Show me the actual curl response from the live AppSail URL after deploy, not a local test.
DO NOT: add any other routes, dependencies, or features beyond this.
```

## Schema creation (Data Store — manual, console GUI only, no DDL via SDK)
Follow `drishti_catalyst_schema.md` batch order exactly: A (lookups) → B (org/people) → C (core case) → E (analytics extension). Skip Batch D depth beyond `CaseStatusMaster` + `ChargesheetDetails.cstype` if short on time.

For each table: Cloud Scale → Data Store → Create Table → add columns matching the doc's type column exactly (VARCHAR/TEXT/INT/DATE/DATETIME/DOUBLE/BOOLEAN). Enable the PII validator on the columns flagged in the schema doc.

## Endpoint build order (each one deployed + verified before moving to the next)
1. `POST /incidents`, `GET /incidents` (CaseMaster CRUD) — unblocks Beta's map
2. `GET /hotspots` — serves Gamma's precomputed DBSCAN cluster output (`HotspotCluster` table/JSON) — this is the real analytical map differentiator, don't let it get skipped in favor of just serving raw incidents
3. `GET /anomalies` — serves Gamma's anomaly-flag output (`AnomalyFlag` table/JSON), for the trend-spike alerts the brief explicitly asks for
3. `GET /incidents/{id}/accused`, `GET /incidents/{id}/victims` — unblocks Gamma's link-analysis work
4. `GET /stations/{id}/resolution` — resolution-loop aggregation (group by `CaseStatusID` / `ChargesheetDetails.cstype` per `UnitID`)
5. Auth — Catalyst Authentication, 2 roles (station / command)

## Antigravity prompt — endpoint task (template, reuse per endpoint)
```
CONTEXT: Block 2, backend endpoint build
CURRENT STATE: [what's already deployed and working]
TASK: Build [ONE endpoint] against the Data Store table(s) [name them]. Use the zcatalyst-sdk
request-bound initialization pattern (per-request, not a global client) — write it as FastAPI
middleware/dependency injection.
CONSTRAINTS: No local file writes (read-only filesystem). Keep response time under 30s. Lazy-import
any heavy library inside the route, not at module level.
DEFINITION OF DONE: Show the actual deployed URL and the real JSON response from a live request —
not a local test result.
DO NOT: touch any other endpoint or add scope beyond this one route.
```

## Errors you will likely hit — and the fix
- **App doesn't respond within cold-start window** → you imported something heavy (pandas/sklearn) at module level. Move the import inside the function that uses it.
- **Import fails only when deployed, works locally** → native C-extension platform mismatch. Re-run the predeploy pip install with the manylinux2014_aarch64 flag, don't just deploy your local venv's packages.
- **SDK calls return null/unauthorized** → you initialized the Catalyst client globally at startup instead of per-request. Fix the init pattern.
- **ZCQL query errors** → it's not full SQL, it's DML-only with a subset of syntax. Check the exact supported clauses before assuming standard SQL works.
- **CORS errors when Beta's Slate-hosted frontend calls your AppSail backend** → different domains. Configure CORS headers on your FastAPI app or route through Catalyst API Gateway.
- **Bulk insert from Gamma's seed data fails partway** → Catalyst likely caps rows per insert call. Chunk the inserts, don't send the whole CSV in one call.

## Git checkpoints
Commit after every working, deployed endpoint — not at the end of the day. Push to `alpha/backend` continuously. Merge to `dev` at the Day 1 evening and Day 2 checkpoints per the master plan.

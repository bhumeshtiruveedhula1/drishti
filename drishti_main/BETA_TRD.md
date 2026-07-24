# Drishti — Beta TRD (Frontend: Map + Consoles + Graph)
Read `PRD.md` and `TEAM_MASTER_PLAN.md` first. This is your task-level detail.

## Your ownership
React app, Leaflet map, Station Console, Command Console, network graph visualization. Build against mock data first — never wait on Alpha's backend to start.

## Hour 0 tasks
1. Clone the repo, checkout `beta/frontend`.
2. Scaffold React + Tailwind + Leaflet + Recharts.
3. Create mock JSON files matching the shapes in `drishti_catalyst_schema.md` (CaseMaster fields, Unit/District fields, resolution metric fields) so your components are already contract-correct when real data arrives.
4. Get a bare Leaflet map rendering with fake pinned incidents on Karnataka's district GeoJSON.

## Antigravity prompt — Hour 0 task
```
CONTEXT: Block 0, frontend scaffold
TASK: Set up a React + Tailwind + Leaflet app. Render a map centered on Karnataka using the
public district GeoJSON, with 10-15 hardcoded mock incident pins (lat/lng, crime category, date)
matching the shape of the CaseMaster table in drishti_catalyst_schema.md.
CONSTRAINTS: Mock data must live in a single separate file (e.g. mockData.js) so swapping to a
real API call later is a one-line change, not a rewrite.
DEFINITION OF DONE: Show me a screenshot/description of the rendered map with visible pins.
DO NOT: wire this to any backend yet — that comes later once Alpha's endpoint is live.
```

## Build order
1. Map with raw incident pins + choropleth by district (this is just visual scaffolding, not the real differentiator)
2. Station Console shell (single-station view)
3. Command Console shell (cross-station view)
4. Swap map's mock data → real `GET /incidents` call once Alpha ships it
5. **Hotspot overlay** — wire to Alpha's `GET /hotspots` endpoint (Gamma's DBSCAN output) and render as a distinct heatmap/highlighted-cluster layer on top of raw pins. This is the actual analytical differentiator — don't let Leaflet's built-in marker-clustering (which just visually groups pins on zoom) stand in for it, they're not the same thing.
6. **Anomaly/trend-spike indicator** — wire to Alpha's `GET /anomalies` endpoint, render as a distinct visual marker (e.g. pulsing red-zone) on the map or a callout in the Command Console — this is the "emerging trend alert" the brief explicitly asks for.
7. Resolution-loop panel (Command Console) — bar/line chart per station, wired to Alpha's endpoint
8. Network graph — `react-force-graph` or `vis-network`, nodes = Accused/Victim/Unit, edges = shared CaseMasterID, wired to Gamma's link-analysis endpoint

## Antigravity prompt — mock-to-real swap (use when Alpha ships an endpoint)
```
CONTEXT: Block 3, swapping mock data for a live endpoint
CURRENT STATE: Map currently renders from mockData.js. Alpha's live endpoint is [URL].
TASK: Replace the mock data source with a fetch call to the live endpoint. Keep the same data
shape/rendering logic — only the source changes.
CONSTRAINTS: Handle loading and error states (the live backend may be slow on cold start,
first request after idle can take a few seconds).
DEFINITION OF DONE: Show the actual rendered map pulling from the live URL, with real incident
data visible, not mock pins.
DO NOT: change map rendering logic, only the data source.
```

## Errors you will likely hit — and the fix
- **CORS error calling Alpha's AppSail backend from your Slate-hosted app** → different domains by default. Tell Alpha, this needs a CORS header on his side or routing through API Gateway — not something you can fix purely on the frontend.
- **Leaflet map doesn't render / shows grey tiles** → usually a missing CSS import (`leaflet/dist/leaflet.css`) or the map container has no explicit height set.
- **GeoJSON district names don't match incident data** → this was flagged early (old spellings like "Bangalore" vs "Bengaluru"). Confirm with Gamma which spelling the seed data uses and match it exactly, or your choropleth will silently drop data with no error.
- **Slow first load after idle / stale data** → AppSail cold starts. Add a loading state, don't assume instant response.
- **Network graph library renders an unreadable tangle** → cap the number of nodes shown for the demo (5–10 example offenders is plenty), don't try to render the full dataset.

## Git checkpoints
Push to `beta/frontend` continuously. At each merge checkpoint (per master plan), pull `dev` first to catch Alpha's latest endpoints before pushing your merge.

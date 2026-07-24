# Drishti — Antigravity Execution Playbook (MAIN — one playbook, used by Alpha, Beta, and Gamma)
This is the controlling document for HOW any of you prompt Antigravity — regardless of who's doing it or whether it goes through ChatGPT first. `drishti_architecture.md`, `TEAM_MASTER_PLAN.md`, `drishti_catalyst_schema.md`, and your own `[NAME]_TRD.md` are reference/context — read them for facts and your specific task list. The rules in THIS file govern behavior, and apply the same way to all three of you.

## Do you need ChatGPT as a relay?
No, not by default. This was originally built for one person routing every prompt through ChatGPT because of a Claude rate limit. Now that each of you has your own TRD with ready-to-use Antigravity prompts, prompt Antigravity directly. Only route through ChatGPT if you personally hit a Claude limit and need a stand-in to keep translating blockers into prompts — it's a fallback, not the default workflow.

## Which Gemini model to use (Antigravity Pro gives you Gemini only — applies to all three of you, pick by task difficulty, not by person)
- **Gemini 3.6 Flash (High)** — default for most work: React components, FastAPI route boilerplate, Tailwind styling, data-cleaning scripts, the bulk of what's in every TRD.
- **Gemini 3.6 Flash (Medium/Low)** — trivial edits, quick fixes, repetitive scaffolding. Use freely, no need to save it for anything.
- **Gemini 3.1 Pro (High)** — reserve for genuinely hard reasoning: Catalyst SDK integration bugs, the DBSCAN/anomaly-threshold tuning logic, the resolution-loop aggregation query, jurisdiction/link-analysis correctness. Pro-tier reasoning matters when correctness is subtle, not when code volume is high.
- Don't trust any model's Catalyst-specific syntax (Data Store SDK, AppSail config) the way you'd trust its React/FastAPI output — Catalyst is a smaller platform in training data terms, hallucination risk is higher there specifically. Cross-check against `drishti_architecture.md`'s constraints section or the actual Catalyst docs before treating it as correct.

## Your role, whichever of you is prompting
You are directing Antigravity, not rubber-stamping it. You do NOT:
- Change architecture, schema, or scope beyond what your current task already specifies
- Accept "should work" as done
- Let Antigravity silently expand scope beyond the stated task

If Antigravity hits an architectural ambiguity not already decided in the reference docs, stop and bring it back to the group (or to Rishik/Claude) rather than letting it guess.

## The one rule that prevents late-stage bugs
**Every prompt targets one vertical slice, never a layer.** Do not prompt "build the backend" or "build the frontend." Prompt one thing that goes from nothing to a live, verified, deployed result — e.g. "make incident creation work end-to-end: one API route, hitting the real Data Store, deployed to AppSail, verified with an actual curl response from the live URL." Layer-by-layer builds hide integration bugs until the layers meet, which is exactly how bugs surface in the last hours.

## Definition of Done — required on every task, no exceptions
A task is NOT done until Antigravity has shown:
1. The actual deployed URL and the actual response/render from it (not "should return X" — the real output)
2. Confirmation the change survived a redeploy, not just a local run
3. Any new dependency verified against AppSail's Linux runtime, not just local success (see architecture doc's dependency-mismatch gotcha)

Reject any report that says "this should work now" without live proof attached. Ask Antigravity to re-run and show the actual result.

## Cadence
- Deploy after every task, not once at the end of a Block.
- At the end of each Block, produce a short **known-issues log** (even if empty) and report it to Rishik before starting the next Block. Nothing gets silently deferred.
- At Block 6 (bug bash), the rule flips: **no new features, only fixes to what's in the demo path.** If Antigravity proposes adding anything, refuse and redirect to fixing existing bugs.

## Prompt template — use this shape every time
```
CONTEXT: [one line — which Block, which vertical slice]
CURRENT STATE: [what already exists/works, from the last known-issues log]
TASK: [the single vertical slice — nothing else]
CONSTRAINTS: [pull relevant ones from drishti_architecture.md's Catalyst constraints section —
  e.g. "lazy-import pandas inside the route, not at module level" if this task touches ML libs]
DEFINITION OF DONE: [live deployed proof required, per the DoD rules above]
DO NOT: [explicitly forbid scope expansion beyond this task]
```

## Escalation rule
- Straightforward retries, syntax fixes, redeploys within the current task: handle without escalating.
- Anything touching schema, architecture, or a decision not already made in the reference docs: stop, report to Rishik with the exact blocker, wait for a call. Do not have Antigravity improvise a workaround for architectural decisions.

## Source of truth for facts
- Full schema: `drishti_catalyst_schema.md`
- Stack, Catalyst gotchas, RBAC shape, PII handling: `drishti_architecture.md`
- Team schedule, roles, git workflow, kill list: `TEAM_MASTER_PLAN.md`
- Your specific tasks and ready-made prompts: your own `[ALPHA|BETA|GAMMA]_TRD.md`
- Full brief-requirement audit / what's built vs deferred: `DRISHTI_BLUEPRINT.md`
If a fact needed isn't in these files, escalate rather than guess.

# Implementation Notes

This document captures project-specific domain rules and implementation decisions that are not fully covered by `PLAN.md`, `SETUP.md`, `CHECKLIST.md`, or `AGENTS.md`. Treat it as the source of truth for how the Scrum Assistant should behave at runtime.

## Product Boundary

This project is an agentic Scrum Assistant, not a project management system. Plane remains the system of record for project work, GitHub remains the source of code activity, Supabase stores assistant memory/context, and n8n owns all user-facing orchestration.

The backend should not become a chat bot. It provides authenticated, typed, reusable tools for n8n:

- Fetch context before a standup.
- Compact commit and standup text into smaller memory objects.
- Persist and retrieve sprint memory.
- Report, update, and resolve blockers.
- Append final standup summaries to Plane cycles.

If a feature can be expressed as visual orchestration in n8n without compromising secrets or Plane access rules, prefer n8n. If a feature needs secrets, typed service access, retries, throttling, or reusable persistence, put it in FastAPI.

## Domain Vocabulary

- **Sprint**: The team-facing Agile term. In Plane API calls this maps to a **cycle**. Backend payloads often use `sprint_id`, but Plane endpoints use `cycle_id`.
- **Participant**: A person who joins a daily scrum. Stored in `participants` with a Plane user id, role, email, and optional GitHub login.
- **Developer**: Participant role that receives commit-driven standup context.
- **BA / QA**: Participant roles that receive generic standup context: blockers and last memory, but no commit personalization.
- **Standup context**: The precomputed per-participant payload used by the n8n Daily Standup agent.
- **Agent memory**: A compacted fact from a standup segment. It is not a transcript.
- **Sprint memory**: Sprint-wide planning facts such as goals, decisions, and boundaries.
- **Blocker**: Anything that slows or stops progress and should be revisited until resolved.

## Runtime Flow

The intended daily flow has three separate phases:

1. **Pre-fetch before standup**
   - n8n cron runs about 45 minutes before the daily scrum.
   - n8n calls `GET /api/context/prefetch` or `POST /api/context/prefetch`.
   - Backend compiles role-aware context from Plane, GitHub, Supabase memory, and active blockers.

2. **Single standup chat session**
   - n8n Chat Trigger starts one shared session.
   - The n8n agent names one participant at a time.
   - A developer gets a personalized question based on commits, blockers, and last summary.
   - BA/QA get generic progress/blocker questions.
   - The agent advances only after the participant says `done`, `next`, or an equivalent completion signal.

3. **Post-participant and post-standup memory**
   - After each participant segment, n8n calls memory compaction and memory upsert.
   - After the whole standup, n8n posts a team summary and calls the Plane cycle-update endpoint.

The backend does not enforce turn-taking. That logic belongs to the n8n agent prompt.

## Standup Question Rules

The canonical scrum questions are:

- What have you done today?
- What will you do tomorrow?
- Any blockers faced today?

The agent should not ask these mechanically if it already knows part of the answer. The point of pre-fetch is to reduce redundant questioning.

Developer question priority:

1. Start with unresolved blockers from previous standups or real-time blocker updates.
2. Mention meaningful commit activity since the previous standup window.
3. Ask for missing context only: intent, current status, next step, and blocker status.
4. If there are no recent commits, ask for a generic progress update and, when available, reference the latest known commit as stale context.

BA/QA question priority:

1. Ask for progress against sprint goals or assigned responsibilities.
2. Ask for blocker/coordination issues.
3. Reference last memory when available.
4. Do not invent commit activity or ask technical commit-specific questions.

## Commit Context Rules

Commit context exists to help the standup agent ask better questions, not to score developer performance.

The backend currently treats the standup window as:

- Current standup: `09:00` in `STANDUP_TIMEZONE`.
- Previous standup: one day before current standup.
- GitHub commits are fetched since the previous standup and filtered to `[previous_standup, current_standup)`.

For developers:

- Match by `github_login` when available.
- Fall back to email matching when no GitHub login is available.
- Fetch commit detail after listing commits so file stats and patches can be available for compaction.
- Store only compacted/lightweight commit rows in `standup_context`.

The backend intentionally strips transient heavy fields before persistence:

- file patch details
- raw file lists
- stats that are useful for summarization but not needed for future context

Commit summaries should be produced before storing final standup context. The current code enforces this in `POST /api/context/store`: commits with `summary = null` are rejected and should be compacted first via `POST /api/context/commits/compact`.

## Memory Rules

Memory is a compressed operational memory, not a log archive.

Store:

- Decisions that affect future sprint work.
- Blockers and changes to blocker status.
- Commit-related progress that explains intent or next action.
- Delivery risks, handoffs, or dependencies.
- Sprint planning facts that should affect future questions.

Do not store:

- Full transcripts.
- Social filler.
- Repeated updates that do not change state.
- Raw commit patches.
- Facts already marked stale unless they become relevant again.

Importance scoring:

- `1`: routine progress update.
- `2`: notable progress, decision, handoff, or scope detail.
- `3`: blocker, escalation, delivery risk, or unresolved dependency.

Memory is idempotently upserted by `(participant_id, sprint_id, standup_date)`. If a segment is compacted twice due to retry, it should update the same memory row rather than create duplicates.

Stale memory should be marked with `stale = true`; do not delete it immediately. Stale memory is excluded from context injection but retained so the team can audit recent assistant behavior.

## Blocker Rules

Every blocker needs a stable key because updates can arrive outside the daily standup. The key is used by n8n and commit-message parsing to identify the same blocker over time.

Blocker lifecycle:

1. `active`: the blocker should be surfaced at the next standup.
2. `active` with updated `last_update`: the blocker has new information but is not resolved.
3. `resolved`: the blocker should stop appearing in active blocker lists.

Rules:

- New blocker reports default to `active`.
- If `last_update` is omitted when reporting a blocker, use the blocker description as the first update.
- Updates should modify `last_update` and bump `updated_at`.
- Resolution should set `status = resolved`, `resolved_at`, and optionally a resolution summary.
- Active blockers should be sorted by most recent update where possible.

Commit-message conventions used by n8n should stay simple:

- `[BLOCKED] <description>` creates a new blocker.
- `[BLOCKER:<key>] <update>` updates an existing blocker.
- `[RESOLVED:<key>] <resolution>` resolves an existing blocker.

## Participant and Role Rules

`participants` is the source of truth for role-aware behavior. Plane project membership alone is not enough because Plane does not know whether someone is a developer, BA, or QA.

Participant mapping rules:

- `plane_user_id` must match the Plane member id.
- `role` controls context behavior.
- `github_login` is preferred for commit matching.
- `email` is a fallback for commit matching.
- inactive participants should not receive standup turns.

If a Plane member is present but missing from `participants`, the backend returns them as `missing_participants` rather than guessing. For demo safety, missing participants can be surfaced to the operator and seeded manually.

## Plane Integration Rules

Plane calls must go through `service/plane_client.py`.

Reasons:

- Plane uses `X-API-Key`, not bearer auth.
- Plane rate limit is 60 requests/minute.
- Plane uses `cycle` internally even though the product language says sprint.
- Plane Cloud uses `/work-items/`, not `/issues/`.

The backend should keep Plane writes narrow. For MVP, the only write is appending a standup summary to a cycle description. Avoid creating or mutating work items unless the feature explicitly requires it.

Cycle summary write behavior:

- Fetch current cycle detail.
- Append the new summary after existing description text.
- Preserve existing description content.
- Return the final description and raw Plane response.

## n8n Ownership Rules

n8n is not just glue code; it is the orchestration layer and buildathon track technology.

n8n should own:

- Cron timing.
- Chat Trigger sessions.
- Participant turn-taking.
- Waiting for `done` / `next`.
- Calling tools in the right order.
- The high-level AI Agent prompt.
- Workflow visibility for the demo.

FastAPI should own:

- Secret-bearing API clients.
- Plane API calls.
- GitHub API calls.
- Supabase writes that need validation or upsert semantics.
- Gemini compaction endpoints used as tools.
- Consistent response envelopes for n8n.

Avoid n8n direct calls to Plane. That would duplicate auth logic, rate-limit handling, and endpoint conventions outside the backend.

## Response Envelope Rules

All n8n-facing endpoints should return:

```json
{"success": true, "data": {}}
```

or:

```json
{"success": false, "error": "message"}
```

Do not return raw arrays or raw service objects from protected endpoints. The only acceptable unauthenticated endpoint is `GET /api/health`.

## Current Context API Shape

The current context flow has three backend operations:

- `POST /api/context/prefetch`: compile full context using JSON body.
- `GET /api/context/prefetch`: compatibility endpoint for n8n HTTP Request query params; returns stored context rows in `data`.
- `POST /api/context/commits/compact`: use Gemini to turn raw commit detail into lightweight commit summaries.
- `POST /api/context/store`: persist pre-fetched context only after commit rows have summaries.

This two-step commit compaction/store design exists because raw commit details can be too large for long-term storage and too noisy for standup prompts.

## Demo Mode vs Production Mode

The project has used demo-friendly pre-seeded data for FinanceFlow Sprint 7. Demo data is useful for predictable judging, but it should not leak into core service abstractions.

Rules:

- Demo data may live in tests, seed scripts, n8n workflows, or explicitly named demo fixtures.
- Production service code should prefer real Plane/GitHub/Supabase calls.
- If an endpoint is temporarily mocked for a demo, document it clearly and revert it before treating the backend as production-ready.

## Error Handling Philosophy

The assistant should degrade in ways that preserve the standup.

Recommended behavior:

- If GitHub has no commits for a developer, continue with an empty commit list and ask a generic update question.
- If GitHub has no recent commits but has older activity, include the latest commit as stale context and mark `has_recent_commits = false`.
- If a participant is missing from the participants table, report them as `missing_participants` and continue for the rest of the team.
- If Plane cycle update fails at the end, keep the chat summary visible and retry the write separately.
- If Gemini compaction fails, return a clear error to n8n so the workflow can retry or fall back to a simpler summary.

Do not silently swallow external API errors. Log them before returning an error envelope or re-raising inside the service layer.

## Security and Privacy Rules

- `.env.agent` is local and must never be committed.
- `SUPABASE_SERVICE_ROLE_KEY` is backend-only.
- n8n may use `SUPABASE_DATABASE_URL` for Postgres node access, but public webhooks must not expose credentials.
- Do not store raw chat transcripts unless explicitly required.
- Do not store raw GitHub patches in Supabase memory tables.
- Do not expose Plane or GitHub tokens to n8n Code nodes when a backend endpoint already exists.

## Invariants

These are assumptions the rest of the system relies on:

- `participant_id` equals Plane user id.
- `sprint_id` equals Plane cycle id unless using demo aliases like `sprint-7`.
- `standup_context` is unique by `(sprint_id, participant_id)`.
- `agent_memory` is unique by `(participant_id, sprint_id, standup_date)`.
- `blockers.key` is stable and unique.
- `participants.role` is one of `developer`, `ba`, or `qa`.
- A stored commit row should have a `summary`; raw commit detail should not be persisted as context.

## Future Implementation Notes

Likely next improvements:

- Add a seed endpoint or script for the FinanceFlow demo participants.
- Add a dedicated `sprint_memory` write endpoint instead of relying on direct n8n Postgres writes.
- Add an explicit demo mode flag if mock context is needed again.
- Add retention cleanup for stale memory older than seven days.
- Add a `standup_date` or `window_start/window_end` field to `standup_context` if multiple standups per day become possible.
- Add partial-success response details to prefetch when one external service fails but other participant context is still available.

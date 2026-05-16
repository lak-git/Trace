# Project Plan — AI Scrum Master (Cursor Buildathon, May 16 2026)

## Track: Best Use of n8n

---

## 1. What We Are Building

A standalone AI Scrum Master agent that automates repetitive tracking and communication across an Agile Scrum team. It is **NOT** built on top of any existing PM platform — it integrates with **Plane Cloud** via its public REST API.

**Key differentiators from existing tools:**
- **n8n-native** — all orchestration visible as visual workflows (track requirement)
- **Commit-driven questioning** — the agent asks about actual code activity, not generic status
- **Real-time blocker capture** — via GitHub webhooks, surfaced at standup without re-explanation
- **Cross-standup persistent memory** — Supabase-backed, with importance-based expiry
- **Plane integration** — no existing standup tool supports Plane
- **Open source** — anyone can self-host

---

## 2. Team

| Person | Role | Ownership |
|--------|------|-----------|
| Lakindu | TBD | TBD |
| Stefan | TBD | TBD |
| Saviskar | TBD | TBD |

---

## 3. Tech Stack

| Layer | Technology | Details |
|-------|-----------|---------|
| Orchestration | **n8n Cloud** (paid, provided at event) | TRACK technology — all workflows in n8n |
| LLM | **Gemini 3.1 Pro / Gemini 3 Flash** | Google AI Studio student credits (1 year) |
| Database | **Supabase PostgreSQL** | Free tier, ap-southeast-1 (Singapore) |
| PM Integration | **Plane Cloud** (app.plane.so) | REST API, X-API-Key auth, 60 req/min |
| Version Control | **GitHub API** | Single shared repo, 5000 req/hr (authenticated) |
| Backend | **Python FastAPI** | Deployed on Google Cloud Run ($300 credits) |
| Frontend/UI | **n8n Chat Trigger** | No Next.js, no React, no Tailwind |

---

## 4. Directory Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py            # Reusable FastAPI dependencies (auth, supabase)
│   │   │   └── endpoints/         # FastAPI route handlers
│   │   ├── core/                  # Config, auth, logging
│   │   ├── model/                 # Pydantic models
│   │   ├── service/               # plane_client, github_client, gemini_client, stores, standup_context
│   │   ├── database.py            # supabase async client (service-role)
│   │   └── main.py                # FastAPI app entry
│   ├── migrations/
│   │   └── 001_initial.sql        # Canonical Supabase schema
│   ├── tests/                     # pytest test suite (conftest.py + 7 test files)
│   ├── pyproject.toml             # Python deps (uv)
│   ├── ruff.toml                  # Ruff linter/formatter config
│   ├── Dockerfile
│   └── .dockerignore
├── n8n_workflows/
│   ├── standup-pre-fetch.json     # Cron: fetch commits, prep context [IN PROGRESS — not yet exported]
│   ├── daily-standup.json         # Chat Trigger: run standup [IN PROGRESS — not yet exported]
│   ├── sprint-planning.json       # Chat Trigger: sprint intake [IN PROGRESS — not yet exported]
│   ├── blocker-webhook.json       # Webhook: real-time blocker capture [IN PROGRESS — not yet exported]
│   └── user-story-gen.json        # STRETCH: story generation [exported]
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Lint + test + build-check on push
│       └── deploy.yml             # Cloud Run deploy on main merge
├── AGENTS.md                  # Cursor agent mode instructions
├── CHECKLIST.md               # Build checklist with phase-by-phase task tracking
├── SETUP.md                   # Pre-flight setup guide for team
├── PLAN.md                    # This file — project overview for team sync
├── .env.agent.example         # Environment variable template
├── repomix.config.json        # Repomix scope config
└── .gitignore
```

---

## 5. Features (Prioritised)

### MVP (Must Work for Demo)

| # | Feature | Workflow | Est. Hours |
|---|---------|----------|------------|
| 1 | **Standup Pre-Fetch** — Cron workflow fetches Plane cycle members, GitHub commits, and active blockers 45min before standup. Stores compiled context per person in Supabase. | `standup-pre-fetch` | 2 |
| 2 | **Daily Standup** — Chat Trigger. Agent greets team, loads pre-fetched context, asks each member tailored questions based on their actual commits. Follows up on blockers. Compacts and stores memory per person. Posts final summary to chat and writes compacted version to Plane cycle description. | `daily-standup` | 5 |
| 3 | **Sprint Planning Intake** — Chat Trigger (Scrum Master only). SM describes sprint goals or pastes notes, agent asks clarifying questions, stores key facts in Supabase for future standup context. | `sprint-planning` | 2 |
| 4 | **Real-time Blocker Capture** — GitHub push webhook. Detects `[BLOCKED]` in commit messages. Captures blocker details in Supabase. Surfaces automatically at next standup with status update option. | `blocker-webhook` | 2 |

### Stretch (If Time Permits)

| # | Feature | Workflow | Est. Hours |
|---|---------|----------|------------|
| 5 | **User Story Generation** — SM describes client needs, agent generates user stories + acceptance criteria, SM reviews/edits, agent creates issues in Plane. | `user-story-gen` | 3 |

### Explicitly Out of Scope (MVP)

- Commit-driven personalisation for BA/QA roles (they get generic context only)
- CI/GitHub Actions integration (deferred)
- Slack/Discord/Telegram bots (n8n Chat Trigger only)
- Rich frontend dashboard (n8n UI only)
- Live audio transcription (manual input only)

---

## 6. Interaction Model

All user-facing interactions happen via **n8n Chat Trigger** (a web chat widget). No external chat platforms.

| Feature | Participants | Interaction Type |
|---------|-------------|-----------------|
| Daily Standup | All 3 (Alice, Bob, Carol) | Single chat room. Agent goes one at a time. Participant says "done" to signal turn to next person. |
| Sprint Planning | Scrum Master only | Private chat. SM describes goals, agent asks clarifying questions. |
| User Story Gen | Scrum Master only (stretch) | Private chat. SM describes needs, agent generates stories for review. |
| Blocker Updates | Individual developer | Via GitHub commit message (`[BLOCKED]`) or direct n8n form/webhook. |

---

## 7. Standup Lifecycle

```
1. n8n CRON (T-45 min)
      │
2. Call backend /api/context/prefetch
      ├── Fetch cycle members from Plane
      ├── Fetch commits per member from GitHub (since last standup)
      ├── Fetch active blockers from Supabase
      └── Store compiled context in standup_context table
      │
3. CHAT TRIGGER opens at standup time
      │
4. For each participant:
      ├── Agent loads their context (commits, blockers)
      ├── Asks tailored question based on actual commits
      ├── Participant responds
      ├── Agent follows up on blockers if mentioned
      └── Agent compacts that segment → stores in agent_memory
      │
5. After all participants:
      ├── Agent posts full summary to the chat room
      └── Agent calls backend to append summary to Plane cycle description
```

---

## 8. Backend API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Health check (no auth) |
| `POST` | `/api/participants` | Seed/upsert a participant (Plane UUID -> role + github_login) |
| `GET` | `/api/participants` | List active participants |
| `GET` | `/api/context/prefetch?project_id=X&cycle_id=Y` | Role-aware fetch of members+commits+blockers; upserts `standup_context` |
| `POST` | `/api/memory/compact` | Compact raw transcript via Gemini; returns summary |
| `POST` | `/api/memory/upsert` | Upsert memory entry (idempotent on participant+sprint+date) |
| `GET` | `/api/memory/{sprint_id}` | Load sprint memory as a single compacted JSON blob |
| `POST` | `/api/plane/cycle-update` | Append standup summary to Plane cycle description |
| `POST` | `/api/blocker/report` | Report a new blocker (creates with stable `key`) |
| `POST` | `/api/blocker/{key}/update` | Append a textual update; bumps `updated_at` |
| `POST` | `/api/blocker/{key}/resolve` | Mark blocker resolved |
| `GET` | `/api/blockers/active?sprint_id=X` | Get active blockers (optionally scoped) |

All endpoints (except `/api/health`) authenticated via `X-Agent-Secret` header.

---

## 9. Supabase Schema

Canonical schema lives in [backend/migrations/001_initial.sql](backend/migrations/001_initial.sql). Run it once in the Supabase SQL editor. Authoritative column definitions also documented in [.cursor/rules/500-database.mdc](.cursor/rules/500-database.mdc).

Tables:

| Table | Purpose | Notes |
|-------|---------|-------|
| `participants` | Plane UUID -> `role` (developer/ba/qa) + `github_login` + `email` | Single source of truth for roles. UNIQUE on `plane_user_id`. |
| `standup_context` | Pre-fetched commit/blocker context per member, per sprint | UNIQUE `(sprint_id, participant_id)` for SDK upserts. |
| `agent_memory` | Compacted standup segments | UNIQUE `(participant_id, sprint_id, standup_date)` for idempotent upsert. `importance` 1-3, `stale` flag. |
| `blockers` | Active + resolved blockers | Stable `key` for commit-message refs (`[BLOCKER:<key>]`), `sprint_id`, `last_update`, auto-bumping `updated_at` trigger. |
| `sprint_memory` | Sprint planning key facts | `category` in (`goal`, `decision`, `boundary`, `note`). |

Access pattern:
- **Backend**: `supabase>=2.4` async SDK, authenticated with `SUPABASE_SERVICE_ROLE_KEY` (bypasses RLS).
- **n8n**: native Postgres node via `SUPABASE_DATABASE_URL`.
- RLS is intentionally NOT enabled for the MVP.

---

## 10. n8n Workflow Details

> **Export status**: Only `user-story-gen.json` is currently exported to the repo.
> `standup-pre-fetch`, `daily-standup`, `sprint-planning`, and `blocker-webhook` are
> partially built in n8n Cloud but not yet exported. Export each via n8n → Download as JSON
> and commit to `n8n_workflows/` when complete.

### Workflow 1: `standup-pre-fetch` (Cron) — IN PROGRESS
- **Trigger**: Cron (default `45 8 * * 1-5`, configurable via `STANDUP_CRON`)
- **Steps**:
  1. HTTP Request → Backend `/api/context/prefetch?project_id=...&cycle_id=...`
  2. Backend returns compiled JSON per participant
  3. Postgres node → Upsert into `standup_context` table

### Workflow 2: `daily-standup` (Chat Trigger) — IN PROGRESS
- **Trigger**: Chat Trigger
- **Nodes**: Chat Trigger → AI Agent (Gemini 3.1 Pro) → Postgres (memory) → HTTP Request (cycle update)
- **AI Agent Tools**:
  - **Postgres** — read standup_context, read/write agent_memory, read blockers
  - **HTTP Request** — call backend `/api/plane/cycle-update`
  - **Workflow** — optionally call sub-workflow (if safe)
- **System Prompt**: Instructs agent on standup protocol: greet, go one-at-a-time, ask commit-driven questions, follow up on blockers, compact after each person, post summary at end.
- **Critical**: This is a single workflow. Do NOT use Workflow Tool with sub-workflows that contain Wait nodes (known data return bug). All turn-taking logic lives in the AI Agent prompt.

### Workflow 3: `sprint-planning` (Chat Trigger) — IN PROGRESS
- **Trigger**: Chat Trigger
- **Nodes**: Chat Trigger → AI Agent → Postgres
- **Flow**: SM describes sprint goals → agent asks clarifying questions → stores key facts in `sprint_memory`
- **Output**: Key facts ready for the standup agent to reference

### Workflow 4: `blocker-webhook` (Webhook) — IN PROGRESS
- **Trigger**: Webhook (GitHub push events)
- **Steps**:
  1. Parse push payload via Code node
  2. Check each commit message for `[BLOCKED]` pattern
  3. If found: Postgres node → Upsert into `blockers` table
  4. If commit message says "resolved" or "fixes": mark blocker as resolved
  5. (Optional) Send notification to n8n channel

### Workflow 5: `user-story-gen` (Chat Trigger) — STRETCH (exported)
- **Trigger**: Chat Trigger
- **Flow**: SM describes client needs → agent generates stories + acceptance criteria → SM reviews → agent creates via Plane API

---

## 11. Build Order (24h Budget)

| Block | Hours | Deliverable | Owner |
|-------|-------|-------------|-------|
| Foundation | 2 | Supabase tables created, Plane workspace seeded, GitHub token ready, n8n credentials configured, Cloud Run service deployed | Lakindu |
| Backend Core | 3 | `plane_client.py`, `github_client.py`, `memory_store.py`, main endpoints (`/context/prefetch`, `/memory/*`, `/blocker/*`) | Stefan |
| Standup Pre-Fetch | 2 | n8n cron workflow + backend endpoint integration | Saviskar + Stefan |
| Daily Standup | 5 | n8n Chat Trigger + AI Agent prompt + turn-taking + memory compact + cycle update | Saviskar + Stefan |
| Sprint Planning | 2 | n8n Chat Trigger + AI Agent + sprint_memory store | Saviskar |
| Blocker Webhook | 2 | GitHub webhook setup + n8n parse + Supabase store | Saviskar |
| Polish + Test | 3 | End-to-end walkthrough, fix edge cases, seed demo data | All |
| Buffer | 3 | Recovery time for anything that breaks | All |
| Demo Prep | 2 | Rehearse 2-min flow, pre-seed Plane with realistic data | All |
| **Total** | **24** | | |

---

## 12. Demo Scenario — FinanceFlow Sprint 7

**Demo Script (2 Minutes)**:

| Time | What Happens | Judge Sees |
|------|-------------|------------|
| :00 | Narrator: "This is Sprint 7 of FinanceFlow. n8n prefetched commits 45min ago." | n8n workflow canvas of `standup-pre-fetch` |
| :15 | "Let's start standup." Click Chat Trigger. | n8n Chat window opens |
| :25 | Agent: "Good morning team! Alice, you're up — I see 2 commits on `feat/biometrics`. How's the FaceID flow looking?" | Commit-driven question |
| :40 | Alice: "Done! Ready for PR review. No blockers." | |
| :50 | Agent: "Noted. Bob — I see you committed a circuit breaker but CI tests are failing. Your blocker from yesterday about the test double — how's that going?" | Cross-standup blocker memory |
| 1:10 | Bob: "Almost there — found a simpler mock approach, should be fixed today." | |
| 1:20 | Agent: "Carol — any updates on the dashboard? Saw your transaction list component." | |
| 1:35 | Carol: "Component's done, starting styling today." | |
| 1:45 | Agent posts summary + writes to Plane. | Cycle description updated in Plane |
| 2:00 | End. | |

---

## 13. Risks (Ranked)

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| **1** | **n8n Workflow Tool + Wait node bug** — calling a sub-workflow with Wait returns pre-wait data, not final output. | HIGH — standup data loss | Single workflow for standup. No sub-workflow calls. All logic in AI Agent prompt. |
| **2** | **Plane API rate limits (60/min)** — burst calls during standup could hit limit. | MEDIUM — cycle update fails | Cache member/cycle data. Batch reads. Keep per-standup calls under 20. |
| **3** | **AI Agent turn-taking prompt fragility** — agent may not reliably detect "done" signal. | MEDIUM — demo stumbles | Prompt engineering: "When the participant says 'done' or 'next', acknowledge and move to the next person." Test explicitly. Add fallback: if no response in ~2min, skip. |
| **4** | **Backend not deployed in time** — Cloud Run deploy issues. | MEDIUM — no backend | Start deployment in first 2 hours. Fallback: if Cloud Run fails, fold backend logic into n8n Code nodes. |

---

## 14. Comparison to Existing Tools

| Tool | Ours | Jira AI Scrum Assistant | n8n Community Template | Asana AI Teammates |
|------|------|------------------------|----------------------|-------------------|
| Standup orchestration | ✅ Chat Trigger | ❌ | ✅ Limited | ❌ |
| Commit-driven questions | ✅ | ❌ | ❌ | ❌ |
| Real-time blocker capture | ✅ | ❌ | ❌ | ❌ |
| Cross-standup memory | ✅ | ❌ | ❌ | ❌ |
| Plane integration | ✅ | ❌ | ❌ | ❌ |
| Story generation | ✅ Stretch | ✅ Core | ❌ | ❌ |
| n8n-native | ✅ TRACK | ❌ | ✅ | ❌ |
| Open source | ✅ | ❌ | ✅ (requires deps) | ❌ |
| Commit tracking | ✅ GitHub API | ❌ | ❌ | ❌ |

---

## 15. Open Decisions (Resolved)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend framework | **None — n8n Chat Trigger** | Track technology must be central. No Next.js/React. |
| Backend framework | **FastAPI** | Async, Pydantic, well-known by team. |
| Plane deployment | **Plane Cloud** | Same API, no Docker overhead. |
| Standup interaction | **Single chat room** | Simpler than separate DMs. One workflow. |
| Demo data | **Pre-seeded** | Too risky to rely on live data in 2-min demo. |
| Workflow architecture | **Single workflow per feature** | Avoids Wait node sub-workflow bug. |
| Sprint Planning mechanism | **Chat Trigger (manual summary)** | No audio transcription — SM pastes notes. |
| Commit tracking timing | **Cron pre-fetch (T-45min)** | Prepares context before standup opens. |
| Team roles in MVP | **Developer + BA + QA** | Developer gets commit-driven personalised questions; BA/QA get generic context (blockers + last memory). Role lives on `participants.role`. |

---

## 16. Team Communication Notes

- All env vars shared via `.env.agent.example` template
- n8n workflow JSONs are checked into `n8n_workflows/` — import into n8n Cloud at event
- Backend deploys to Google Cloud Run — URL shared in n8n HTTP Request nodes
- Single shared GitHub repo for demo — all 3 push commits
- Supabase tables created by whomever gets there first — SQL in SETUP.md
- **Before day starts**: SETUP.md steps should be completed by all
- **Day of**: Build order in section 11. Parallelise where possible

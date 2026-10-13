# Trace

An agentic Scrum assistant that runs your daily standup from what your team actually committed, and remembers what was said yesterday. Aimed to bring value by automating repetitive and labor intensive tasks of Project Managers, Business Analysts and Scrum Masters alike.

Built in 24 hours at the Cursor Buildathon (May 16, 2026) for the Best Use of n8n track.

## The problem

Daily standups waste time on questions the team's tools can already answer. A developer pushed four commits yesterday, but the facilitator still asks "what did you work on?" A blocker came up in a commit message on Tuesday, and by Thursday nobody remembers it. The notes live in someone's head, or nowhere.

## The idea

Trace joins the standup as a facilitator. Before the meeting it pulls each person's commits, open blockers and last standup summary. During the meeting it asks each person about their own work instead of generic questions. Afterwards it compresses what was said into a small memory entry and writes the team summary back to the sprint in Plane.

- **Commit-driven questions.** A developer is asked about the commits they pushed since the last standup. BA and QA members get blocker and progress questions, with no commit context.
- **Blocker tracking.** Blockers have a stable key and are raised again at every standup until someone resolves them. The plan was to capture them from commit messages (`[BLOCKED]`, `[BLOCKER:<key>]`, `[RESOLVED:<key>]`).
- **Memory across standups.** Each person's segment is compacted with Gemini into a short entry with an importance score from 1 to 3. Old entries are marked stale, not deleted.
- **Sprint planning intake.** The Scrum Master describes sprint goals in a chat. Trace asks clarifying questions and stores goals, decisions and boundaries for later standups.
- **User story generation (stretch).** The Scrum Master describes what a client wants, and Trace drafts user stories with acceptance criteria and can create them in Plane.

Trace is not a project management tool. Plane stays the system of record, GitHub supplies code activity, Supabase holds the assistant's memory, and n8n runs the conversations.

## How it works

```
                  n8n Cloud
  ┌───────────────┬──────────────────┬──────────────────┐
  │ Pre-fetch     │ Daily standup    │ Sprint planning  │
  │ (cron, T-45m) │ (Chat Trigger)   │ (Chat Trigger)   │
  └───────┬───────┴────────┬─────────┴────────┬─────────┘
          │  HTTP + X-Agent-Secret            │
          ▼                                   ▼
  ┌──────────────────────────────────────────────────┐
  │ FastAPI backend (Cloud Run)                      │
  │ plane_client · github_client · gemini_client     │
  │ participant / blocker / memory stores            │
  └─────┬──────────────┬──────────────┬──────────────┘
        ▼              ▼              ▼
     Plane Cloud    GitHub API    Supabase Postgres
```

A standup runs in three phases:

1. **Pre-fetch.** An n8n cron job runs 45 minutes before the standup and calls the backend. The backend lists the Plane cycle members, fetches each developer's commits since the previous standup from GitHub, summarises them with Gemini, and stores the result per person in `standup_context`.
2. **Standup.** An n8n Chat Trigger opens one shared chat. The AI agent names one participant at a time, loads their context from Postgres, asks about their commits and blockers, and moves on when they say `done`. Turn-taking lives in the agent prompt, not in the backend.
3. **Wrap-up.** After each person, the transcript segment is compacted and upserted into `agent_memory`. After the last person, the agent posts a team summary and appends it to the Plane cycle description.

The split between n8n and the backend is deliberate. n8n owns cron timing, chat sessions, turn-taking and the agent prompts. The backend owns anything that needs secrets, retries, rate limiting or typed persistence. Plane is only ever called through `service/plane_client.py`, which handles the `X-API-Key` header and the 60 requests/minute limit.

## What we built

### The Backend

All endpoints sit under `/api` and require an `X-Agent-Secret` header, except the health check.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Health check, no auth |
| `POST`, `GET` | `/api/participants` | Upsert and list participants (Plane user to role and GitHub login) |
| `GET`, `POST` | `/api/context/prefetch` | Compile role-aware context from Plane, GitHub, blockers and memory |
| `POST` | `/api/context/commits/compact` | Summarise commits with Gemini |
| `POST` | `/api/context/store` | Store compiled standup context (rejects uncompacted commits) |
| `POST` | `/api/memory/compact` | Compact a standup transcript segment |
| `POST` | `/api/memory/upsert` | Idempotent upsert on participant, sprint and date |
| `GET` | `/api/memory/{sprint_id}` | Load sprint memory |
| `POST` | `/api/blocker/report` | Create a blocker with a stable key |
| `POST` | `/api/blocker/{key}/update` | Add an update to a blocker |
| `POST` | `/api/blocker/{key}/resolve` | Resolve a blocker |
| `GET` | `/api/blockers/active` | List active blockers |
| `POST` | `/api/plane/cycle-update` | Append a standup summary to a Plane cycle |
| `POST` | `/api/plane/work-item` | Create a work item (used by story generation) |

The rest of the backend:

- Supabase schema in `backend/migrations/001_initial.sql`: `participants`, `standup_context`, `agent_memory`, `blockers`, `sprint_memory`.
- Async clients for Plane, GitHub and Gemini, with `tenacity` retries.
- 74 pytest test functions covering auth, participants, context, memory, blockers, Plane and health.
- GitHub Actions for lint and tests (`ci.yml`) and for Cloud Run deploys through Workload Identity Federation (`deploy.yml`).

### n8n workflows

| Workflow | Trigger | Status in this repo |
|---|---|---|
| `standup-pre-fetch-optimized` | Schedule | Exported |
| `daily-standup` | Chat Trigger | Exported |
| `sprint-planning` | Chat Trigger | Exported |
| `user-story-gen` | Chat Trigger | Exported |
| `blocker-webhook` | GitHub push webhook | Not exported. The backend endpoints exist, the workflow was unfinished. |

The n8n side was only partly working when time ran out. Treat the exported JSON as a starting point you will need to reconnect to your own credentials.

## What went wrong

The only user interface was the n8n Chat Trigger. We chose that to keep n8n central to the track, and it was the wrong call for a product. The chat widget is a plain text box with no concept of participants, turns or a live blocker list, so a multi-person standup feels awkward. A small web frontend over the same backend would have fixed most of that, and it was ruled out in our own rules (`No frontend framework`).

The backend was finished and tested, but the n8n workflows were only partly working by the deadline, and the event conditions did not help. We did not place.

## Demo scenario

The seed data models a mobile banking app called FinanceFlow in Sprint 7, with three developers (Alice, Bob and Carol), pre-seeded commits, a blocker and a Plane cycle. The intended two-minute demo was: trigger the pre-fetch, open the standup chat, get a question built from a real commit, mention a blocker and see it followed up, then watch the summary land in Plane. `SETUP.md` has the full script.

## Getting started

You need Python 3.12+, [uv](https://docs.astral.sh/uv/), and accounts for Supabase, Plane Cloud, n8n Cloud, a Gemini API key, and a GitHub token with `repo` scope.

```bash
git clone https://github.com/lak-git/Trace.git
cd Trace
cp .env.agent.example .env.agent      # fill in your values
cd backend
uv sync
uv run uvicorn app.main:app --reload  # http://localhost:8000
```

1. Run `backend/migrations/001_initial.sql` in the Supabase SQL editor.
2. Create a Plane workspace, project and cycle, and generate a personal access token (`plane_api_...`).
3. Seed participants through `POST /api/participants` so each Plane member has a role and GitHub login.
4. Import the JSON files from `n8n_workflows/` into n8n, create the Gemini, Postgres and HTTP credentials, and point the HTTP nodes at your backend URL.

`SETUP.md` has the long version, including the manual Cloud Run deploy.

### Environment variables

| Variable | Used by |
|---|---|
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | Backend |
| `SUPABASE_ANON_KEY`, `SUPABASE_DATABASE_URL` | n8n |
| `PLANE_API_BASE_URL`, `PLANE_API_TOKEN`, `PLANE_WORKSPACE_SLUG`, `PLANE_PROJECT_ID` | Backend |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | Backend |
| `GITHUB_TOKEN`, `GITHUB_REPO` | Backend |
| `AGENT_N8N_WEBHOOK_SECRET` | Backend and n8n |
| `STANDUP_CRON`, `STANDUP_TIMEZONE` | n8n |

### Development

```bash
uv run pytest          # tests
uv run ruff check .    # lint
uv run ruff format .   # format
```

## Tech stack

| Layer | Technology |
|---|---|
| Orchestration and UI | n8n Cloud (Chat Trigger, AI Agent, Schedule Trigger) |
| LLM | Google Gemini via AI Studio |
| Backend | Python 3.12, FastAPI, httpx, tenacity, Pydantic v2 |
| Database | Supabase Postgres |
| Integrations | Plane Cloud REST API, GitHub API |
| Deployment | Docker, Google Cloud Run, GitHub Actions |
| Tooling | uv, ruff, pytest, Cursor |

## What we would do next

- Build a small web frontend for the standup room, served by the backend.
- Finish and export the `blocker-webhook` workflow so blockers are captured from commits as designed.
- Give BA and QA members context beyond blockers and last memory.
- Add Slack or Teams as a chat surface.

## License

Apache-2.0. Add a `LICENSE` file with the full text before publishing.

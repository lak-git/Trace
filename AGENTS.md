# AGENTS.md
# Cursor Agent Mode Instructions — Agentic Scrum Assistant (Cursor Buildathon)

Read this file entirely before executing any multi-step autonomous task.

---

## Architecture Overview

Standalone Agentic Scrum Assistant system. NOT a fork or plugin of Plane or any PM tool.
Integrates with Plane Cloud via REST API. All orchestration in n8n (track technology).

```
┌──────────────────────────────────────────────────────────────────┐
│                        n8n Cloud (TRACK)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Pre-Fetch   │  │ Daily Standup│  │ Sprint Planning        │  │
│  │ (cron)      │  │ (Chat Trigger)│  │ (Chat Trigger)         │  │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬──────────────┘  │
│         │                │                     │                 │
│         └──────────┬─────┘─────────────────────┘                 │
│                    │                                              │
│              ┌─────▼──────┐                                       │
│              │  FastAPI   │  Google Cloud Run                     │
│              │  Backend   │                                       │
│              └─────┬──────┘                                       │
│                    │                                              │
├────────────────────┼──────────────────────────────────────────────┤
│                    ▼                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                           │
│  │  Plane   │ │  GitHub  │ │ Supabase │                           │
│  │  Cloud   │ │   API    │ │ Postgres │                           │
│  └──────────┘ └──────────┘ └──────────┘                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## Commands

```bash
uv sync                        # Install Python dependencies
uv run uvicorn app.main:app    # Start FastAPI dev server (default :8000)
uv run pytest                  # Run tests
uv run ruff check .            # Lint
uv run ruff format .           # Format
```

---

## Directory Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/endpoints/     # FastAPI route handlers
│   │   ├── core/              # Config, auth, DB session
│   │   ├── model/             # Pydantic models
│   │   ├── service/           # Business logic (plane, github, memory)
│   │   ├── database.py        # Supabase async connection
│   │   └── main.py            # FastAPI app entry
│   ├── pyproject.toml         # Python deps (uv)
│   ├── Dockerfile
│   ├── .dockerignore
│   └── .env.example
├── n8n_workflows/
│   ├── standup-pre-fetch.json     # Cron: fetch commits, prep context
│   ├── daily-standup.json         # Chat Trigger: run standup
│   ├── sprint-planning.json       # Chat Trigger: sprint intake
│   ├── blocker-webhook.json       # Webhook: real-time blocker capture
│   └── user-story-gen.json        # STRETCH: story generation
├── AGENTS.md
├── SETUP.md
├── .env.agent.example
├── repomix.config.json
└── .gitignore
```

---

## Pre-Flight Checklist

1. Identify which files will be created or modified.
2. If modifying outside `backend/` or `n8n_workflows/`, state the file path and justify.
3. Search for existing implementations before creating new files.
4. Read the full content of any file before modifying it.

---

## Hard Rules

- **Never auto-commit.** Output the message and stop.
- **Never inline credentials.** All secrets in `.env.agent`, env vars in `.env.agent.example`.
- **Never call Plane API directly from n8n.** All calls through FastAPI `service/plane_client.py`.
- **Never generate test files unless explicitly asked.**
- **One responsibility per file.**
- **Plane API auth header is `X-API-Key`.** Token format: `plane_api_<token>`.
  Rate limit: 60 req/min — implement throttling in `plane_client.py`.
- **No frontend framework.** n8n Chat Trigger is the UI. No Next.js, no React, no Tailwind.

---

## Environment Variables Reference

All agent env vars live in `.env.agent`. The `.env.example` file must always match.

| Variable | Purpose |
|---|---|
| `SUPABASE_DATABASE_URL` | PostgreSQL connection string (pooler, port 5432) |
| `PLANE_API_BASE_URL` | `https://api.plane.so/api/v1` |
| `PLANE_API_TOKEN` | Plane API key — `X-API-Key` header, `plane_api_<token>` |
| `PLANE_WORKSPACE_SLUG` | Workspace slug from app.plane.so URL |
| `PLANE_PROJECT_ID` | Default project UUID |
| `GEMINI_API_KEY` | Google AI Studio API key (student credits) |
| `GEMINI_MODEL` | Model name, e.g. `gemini-3.1-pro` or `gemini-3-flash` |
| `STANDUP_CRON` | Cron expression for pre-fetch (default: `45 8 * * 1-5`) |
| `STANDUP_TIMEZONE` | Timezone for standup scheduling |
| `AGENT_N8N_WEBHOOK_SECRET` | Shared secret for n8n → agent webhooks |
| `GITHUB_TOKEN` | GitHub personal access token (repo scope) |
| `GITHUB_REPO` | Shared repo in format `owner/repo` |

---

## Backend Service Layer

| Module | Responsibility |
|---|---|
| `service/plane_client.py` | All Plane REST API calls — typed async, Pydantic returns |
| `service/github_client.py` | Fetch commits per user, parse commit messages |
| `service/memory_store.py` | Read/write/upsert agent memory in Supabase |
| `service/memory_schema.py` | Pydantic models for memory entries |
| `service/standup_context.py` | Compile per-member context for standup |

---

## n8n Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `standup-pre-fetch` | Cron (T-45min) | Fetch members+commits+blockers → store in Supabase |
| `daily-standup` | Chat Trigger | Load context → run standup per member → compact → store |
| `sprint-planning` | Chat Trigger | Scrum Master pastes sprint details → agent stores key facts |
| `blocker-webhook` | Webhook (GitHub push) | Detect `[BLOCKED]` commits → store/update blocker in Supabase |
| `user-story-gen` | Chat Trigger (stretch) | SM describes client needs → agent generates stories + criteria |

---

## Standup Lifecycle

```
1. n8n cron trigger (45min before standup)
      │
2. Call backend /api/context/prefetch
      ├── Fetch cycle members from Plane
      ├── Fetch commits per member from GitHub (since last standup)
      ├── Fetch active blockers from Supabase
      └── Store compiled context in standup_context table
      │
3. Chat Trigger opens at standup time
      │
4. For each participant:
      ├── Agent greets, loads their context (commits, blockers)
      ├── Asks tailored question based on actual activity
      ├── Participant responds
      ├── Agent follows up on blockers if mentioned
      └── Agent compacts that segment → stores in memory
      │
5. After all participants:
      ├── Agent posts full summary to the room
      └── Agent writes compacted summary → Plane cycle description
```

---

## Demo Scenario (FinanceFlow)

See SETUP.md for the full demo script. Key points:
- Product: mobile banking app "FinanceFlow", Sprint 7
- Team: 3 developers (Alice, Bob, Carol)
- Pre-seeded commits, blockers, and sprint data in Plane
- 2-minute demo: n8n workflow → chat standup → commit-driven questions → blocker follow-up → Plane update

---

## Plane API Endpoints Used

Base: `https://api.plane.so/api/v1/workspaces/{slug}/`

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/projects/` | List projects |
| `GET` | `/project-members/` | List workspace members |
| `GET` | `projects/{pid}/project-members/` | List project members |
| `GET` | `projects/{pid}/cycles/` | List cycles |
| `GET` | `projects/{pid}/cycles/{cid}/` | Get cycle detail |
| `PATCH` | `projects/{pid}/cycles/{cid}/` | Update cycle (standup summary) |
| `GET` | `projects/{pid}/cycles/{cid}/cycle-issues/` | List issues in cycle |
| `GET` | `projects/{pid}/work-items/` | List all work items |
| `GET` | `projects/{pid}/work-items/{iid}/` | Get work item detail |
| `GET` | `projects/{pid}/work-items/{iid}/activities/` | Issue activity log |
| `GET` | `projects/{pid}/states/` | List states |

Auth: `X-API-Key: plane_api_<token>`. Rate limit: 60 req/min. Pagination: cursor-based.

---

## On Errors During Tasks

If you encounter an error mid-task:
1. Stop immediately. Report what was done, what failed, and the current state.
2. Suggest the specific next step.
3. Do not proceed autonomously past a failure.

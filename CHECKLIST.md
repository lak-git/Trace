# Buildathon Checklist — AI Scrum Master
## May 16, 2026 | Track: Best Use of n8n

**Legend:** `[  ]` = not started · `[~]` = in progress · `[X]` = done

---

## Phase 0 — Pre-Buildathon (Complete Before 10:00)

### 0.1 — Shared Accounts & Repo
- [ ] Create GitHub organization / repo `ai-scrum-master` (Lakindu)
- [ ] Add Stefan and Saviskar as collaborators
- [ ] Set up branch protection: `main` requires PR, `dev` is unprotected
- [ ] Everyone clones + verifies `uv sync` works

### 0.2 — Supabase
- [ ] Create Supabase project (region: ap-southeast-1)
- [ ] Copy pooler connection string
- [ ] Run SQL to create 4 tables:
  - [ ] `standup_context`
  - [ ] `agent_memory`
  - [ ] `blockers`
  - [ ] `sprint_memory`

### 0.3 — Plane Cloud
- [ ] Create workspace at https://app.plane.so
- [ ] Create project (e.g. "FinanceFlow")
- [ ] Create cycle "Sprint 7"
- [ ] Create 3+ issues, one per member
- [ ] Configure states: Backlog, In Progress, In Review, Done, Blocked
- [ ] Generate personal access token (starts with `plane_api_`)

### 0.4 — GitHub Token
- [ ] Generate classic PAT with `repo` scope (or fine-grained: `contents:read`, `metadata:read`)
- [ ] Share token with team for `.env.agent`

### 0.5 — n8n Cloud (provided at event)
- [ ] Log in to https://app.n8n.cloud
- [ ] Create credentials for:
  - [ ] Google Gemini (student API key)
  - [ ] Postgres (Supabase connection string)
  - [ ] HTTP Request (for Plane / backend calls)

### 0.6 — Google Cloud
- [ ] Enable Cloud Run API + Artifact Registry API
- [ ] Confirm billing is active ($300 credits)
- [ ] Note project ID and region

### 0.7 — Environment Variables
- [ ] Copy `.env.agent.example` → `.env.agent`
- [ ] Fill in all 12 variables with real values
- [ ] Verify `.env.agent` is in `.gitignore`

---

## Phase 1 — Backend Scaffold (Hours 0–2)
**Owner: Stefan | Depends on: 0.2, 0.3, 0.4, 0.7**

### 1.1 — Project Structure
- [ ] Create `backend/` directory tree
- [ ] Create `backend/pyproject.toml` (deps: `fastapi`, `uvicorn`, `httpx`, `asyncpg`, `pydantic-settings`, `google-genai`, `python-dotenv`)
- [ ] Run `uv sync` — installs all dependencies
- [ ] Create `backend/app/__init__.py`

### 1.2 — Core Config & DB
- [ ] `backend/app/core/__init__.py`
- [ ] `backend/app/core/config.py` — load env vars via `pydantic-settings`
- [ ] `backend/app/core/auth.py` — `X-Agent-Secret` dependency
- [ ] `backend/app/core/deps.py` — reusable FastAPI dependencies
- [ ] `backend/app/database.py` — async Supabase connection pool

### 1.3 — Pydantic Models
- [ ] `backend/app/model/__init__.py`
- [ ] `backend/app/model/standup.py` — StandupContext, CompiledContext
- [ ] `backend/app/model/memory.py` — AgentMemory, MemoryUpsert
- [ ] `backend/app/model/blocker.py` — BlockerCreate, BlockerResponse
- [ ] `backend/app/model/plane.py` — PlaneMember, PlaneCycle, PlaneIssue

### 1.4 — Service Layer
- [ ] `backend/app/service/__init__.py`
- [ ] `backend/app/service/plane_client.py` — typed async Plane API client with rate-limit throttle (60 req/min)
- [ ] `backend/app/service/github_client.py` — fetch commits per user by email since timestamp
- [ ] `backend/app/service/memory_store.py` — read/write/upsert agent_memory and standup_context
- [ ] `backend/app/service/standup_context.py` — compile per-member context (commits + blockers + last summary)

### 1.5 — API Endpoints
- [ ] `backend/app/api/__init__.py`
- [ ] `backend/app/api/endpoints/__init__.py`
- [ ] `backend/app/api/endpoints/health.py` — `GET /api/health`
- [ ] `backend/app/api/endpoints/context.py` — `GET /api/context/prefetch`
- [ ] `backend/app/api/endpoints/memory.py` — `POST /api/memory/compact`, `POST /api/memory/upsert`, `GET /api/memory/{sprint_id}`
- [ ] `backend/app/api/endpoints/plane.py` — `POST /api/plane/cycle-update`
- [ ] `backend/app/api/endpoints/blocker.py` — `POST /api/blocker/report`, `GET /api/blockers/active`

### 1.6 — App Entry & Router
- [ ] `backend/app/main.py` — FastAPI app creation, include routers, CORS, lifespan

### 1.7 — Verify
- [ ] `uv run uvicorn app.main:app` starts without errors
- [ ] `curl localhost:8000/api/health` returns 200

---

## Phase 2 — Deployment & CI/CD (Hours 2–3)
**Owner: Lakindu | Depends on: 1.6**

### 2.1 — Docker
- [ ] `backend/Dockerfile` — Python 3.12 slim, uv install, uvicorn CMD
- [ ] `backend/.dockerignore` — exclude `__pycache__`, `.venv`, `.env.*`

### 2.2 — GitHub Actions CI
- [ ] Create `.github/workflows/ci.yml`
- [ ] Trigger on push to `dev` and `main`
- [ ] Job: `lint` — `ruff check .`
- [ ] Job: `test` — `pytest` (if tests exist)
- [ ] Job: `build-check` — build Docker image (without deploying)

### 2.3 — GitHub Actions CD
- [ ] Add `deploy` job to same workflow
- [ ] Conditional: `if: github.ref == 'refs/heads/main'`
- [ ] Uses `google-github-actions/auth` + `google-github-actions/deploy-cloudrun`
- [ ] Pass env vars via GitHub Secrets (or `.env.cloud.json`)

### 2.4 — Cloud Run Deploy (First Time)
- [ ] Push `dev` branch
- [ ] Merge `dev` → `main`
- [ ] Verify Cloud Run deploy succeeds
- [ ] Note endpoint URL
- [ ] Test: `curl <cloud-run-url>/api/health` returns 200

---

## Phase 3 — Pre-Fetch Workflow (Hours 3–5)
**Owner: Saviskar + Stefan | Depends on: 1.5, 2.4**

### 3.1 — Backend: `/api/context/prefetch`
- [ ] Read cycle members from Plane (`plane_client.get_cycle_members`)
- [ ] For each member: fetch GitHub commits since last standup (`github_client.get_commits_by_email`)
- [ ] For each member: fetch active blockers from Supabase
- [ ] Compile context object per member
- [ ] Upsert into `standup_context` table
- [ ] Return compiled context as JSON

### 3.2 — n8n: `standup-pre-fetch.json`
- [ ] Cron trigger node (default: `45 8 * * 1-5`)
- [ ] HTTP Request node → `POST /api/context/prefetch?project_id=X&cycle_id=Y`
- [ ] Postgres node → verify data landed in `standup_context`
- [ ] Add error handling (retry 1x on failure)
- [ ] Import and test in n8n Cloud

---

## Phase 4 — Daily Standup Workflow (Hours 5–10)
**Owner: Saviskar + Stefan | Depends on: 3.1**

### 4.1 — Backend: `/api/memory/compact`
- [ ] Accept raw transcript text
- [ ] Call Gemini to compact into 2-3 sentence summary
- [ ] Return compacted summary

### 4.2 — Backend: `/api/memory/upsert`
- [ ] Accept `participant_id`, `sprint_id`, `standup_date`, `summary`, `importance`
- [ ] Upsert into `agent_memory` table
- [ ] Return created/updated record

### 4.3 — Backend: `/api/plane/cycle-update`
- [ ] Accept `cycle_id` and `summary_text`
- [ ] Fetch current cycle description from Plane
- [ ] Append new summary to existing description
- [ ] PATCH cycle with updated description

### 4.4 — n8n: `daily-standup.json`
- [ ] Chat Trigger node
- [ ] AI Agent node (Gemini 3.1 Pro / 3 Flash)
- [ ] Tools available to AI Agent:
  - [ ] Postgres: read `standup_context` for current sprint
  - [ ] Postgres: read `blockers` (active)
  - [ ] Postgres: write to `agent_memory`
  - [ ] HTTP Request: `POST /api/memory/compact`
  - [ ] HTTP Request: `POST /api/plane/cycle-update`

### 4.5 — System Prompt (in n8n AI Agent)
- [ ] Greet team: "Good morning team!"
- [ ] Go one person at a time
- [ ] For each: load their commits + blockers from pre-fetched context
- [ ] Ask about specific commits (e.g. "I see 2 commits on feat/biometrics...")
- [ ] Follow up if blocker exists from yesterday
- [ ] On "done" / "next" → compact that segment, store to agent_memory
- [ ] After all done → post full summary to chat
- [ ] Call `/api/plane/cycle-update` to write to Plane

### 4.6 — Test Standup Flow
- [ ] Trigger Chat Trigger manually
- [ ] Walk through all 3 members
- [ ] Verify memory stored in Supabase
- [ ] Verify Plane cycle description updated

---

## Phase 5 — Sprint Planning Workflow (Hours 10–12)
**Owner: Saviskar | Depends on: 1.5, 2.4**

### 5.1 — Backend: sprint memory endpoints (if separate)
- [ ] Confirm `POST /api/memory/upsert` handles sprint_memory table too, OR create dedicated endpoint

### 5.2 — n8n: `sprint-planning.json`
- [ ] Chat Trigger node (Scrum Master only)
- [ ] AI Agent node
- [ ] System prompt: store sprint goals, decisions, boundaries in `sprint_memory`
- [ ] Postgres tool: write to `sprint_memory`
- [ ] Test: SM describes Sprint 7 goals → verify in Supabase

---

## Phase 6 — Blocker Webhook (Hours 12–14)
**Owner: Saviskar | Depends on: 1.5, 2.4**

### 6.1 — Backend: `/api/blocker/report`
- [ ] Accept `participant_id`, `description`, `source`, optional `github_url`
- [ ] Insert into `blockers` table
- [ ] Return created record

### 6.2 — Backend: `/api/blockers/active`
- [ ] Accept optional `project_id`, `cycle_id`
- [ ] Return active blockers

### 6.3 — n8n: `blocker-webhook.json`
- [ ] Webhook node (GitHub push events)
- [ ] Code node: parse push payload, check each commit for `[BLOCKED]`
- [ ] If found: HTTP Request → `POST /api/blocker/report`
- [ ] If commit contains "resolved" or "fixes": mark blocker as resolved (or call update endpoint)
- [ ] Test: push a commit with `[BLOCKED]` → verify in Supabase

---

## Phase 7 — Polish & E2E Testing (Hours 14–17)
**Owner: All**

- [ ] Seed Plane with realistic demo data (Sprint 7, 3 issues, "In Progress")
- [ ] Seed GitHub with demo commit history (3 members, 2 commits each)
- [ ] Run full standup from end to end
- [ ] Fix edge cases:
  - [ ] What if a member has no commits? (Agent asks "any updates?")
  - [ ] What if no active blockers? (Agent skips blocker question)
  - [ ] What if Plane API times out? (Backend returns partial context)
  - [ ] What if GitHub returns 0 commits for someone? (Return empty list, not error)
- [ ] Test blocker webhook with `[BLOCKED]` commit
- [ ] Test sprint planning intake

---

## Phase 8 — Demo Prep (Hours 17–19)
**Owner: All**

- [ ] Rehearse 2-minute demo script
- [ ] Pre-seed all demo data (Plane + GitHub + Supabase)
- [ ] Verify n8n workflows are imported and credential-bound
- [ ] Verify Cloud Run endpoint is live
- [ ] Practice turn-taking in standup chat (Alice → Bob → Carol)
- [ ] Practice blocker follow-up scenario
- [ ] Have a backup plan: if Cloud Run is down, run backend locally and point n8n to ngrok

---

## Phase 9 — Buffer (Hours 19–22)
- [ ] Handle any unexpected breakage
- [ ] Fix prompt issues (agent doesn't follow turn order, skips members, etc.)
- [ ] Update AGENTS.md with any new learnings

---

## Phase 10 — Presentation (Hours 22–24)
- [ ] Final walkthrough with judges
- [ ] Show n8n canvas (pre-fetch workflow)
- [ ] Run standup via Chat Trigger
- [ ] Show Plane cycle description after update
- [ ] Q&A prep: architecture decisions, why no sub-workflows, demo data realism

---

## Quick Reference — Key Commands

```bash
# Backend
uv sync                          # Install deps
uv run uvicorn app.main:app      # Local dev server
uv run pytest                    # Run tests
uv run ruff check .              # Lint
uv run ruff format .             # Format

# Docker
docker build -t ai-sm backend/   # Build image locally
docker run -p 8000:8000 ai-sm    # Run locally

# Deploy (CI does this, but manual fallback)
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/$PROJECT/cloud-run-source-deploy/ai-sm backend/
gcloud run deploy ai-sm --image asia-southeast1-docker.pkg.dev/$PROJECT/cloud-run-source-deploy/ai-sm --region asia-southeast1 --allow-unauthenticated
```

## Quick Reference — Branch Strategy

```
feature/* → PR → dev (CI: lint + test + build-check)
dev → PR → main (CI: lint + test + build-check → deploy to Cloud Run)
```

Cloud Run always reflects `main`. Team tests backend locally with `uv run uvicorn`.

## Quick Reference — n8n Workflow Tools vs. Endpoints

| n8n Needs | Backend Endpoint | When Called |
|---|---|---|
| Pre-fetch context | `GET /api/context/prefetch` | Cron (T-45min) |
| Compact transcript | `POST /api/memory/compact` | After each standup segment |
| Store memory | `POST /api/memory/upsert` | After each compact |
| Load sprint context | `GET /api/memory/{sprint_id}` | Standup start |
| Append to Plane cycle | `POST /api/plane/cycle-update` | Standup end |
| Report blocker | `POST /api/blocker/report` | Webhook trigger |
| Get active blockers | `GET /api/blockers/active` | Pre-fetch + standup |

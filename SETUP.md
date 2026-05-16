# Buildathon Setup Guide
# AI Scrum Master — Cursor Buildathon, May 16

Complete this **before** the buildathon starts.
All three team members should run through it independently.
Estimated time: 30 minutes.

---

## Prerequisites

```bash
git --version          # Any recent version
python3 --version      # 3.11+
pip install uv         # Python package manager
docker --version       # For local testing (optional)
```

---

## Step 1 — Clone the Repository

Only one person (Lakindu) creates the repo. Stefan and Saviskar clone it.

```bash
git clone https://github.com/<your-org>/ai-scrum-master.git
cd ai-scrum-master
```

Branch strategy (agree before start):
```
main          — stable, demo-ready
dev           — active development
features/*    — individual feature branches
```

---

## Step 2 — Set Up Supabase

1. Go to https://supabase.com → Create new project
2. Region: **ap-southeast-1** (Singapore)
3. After creation, go to Project Settings → API and copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY` (BACKEND ONLY — keep secret)
4. Go to Project Settings → Database → Connection pooling, copy the **pooler**
   connection string (port 5432) → `SUPABASE_DATABASE_URL` (used by n8n's
   Postgres node, not by the backend).
5. Open the SQL editor and run [backend/migrations/001_initial.sql](backend/migrations/001_initial.sql)
   in one go. It creates all five tables (`participants`, `standup_context`,
   `agent_memory`, `blockers`, `sprint_memory`) with the required UNIQUE
   constraints, indexes, and the `blockers.updated_at` trigger.

RLS is intentionally NOT enabled on agent tables for the MVP (the backend uses
the service role key and n8n uses a direct Postgres connection, both bypass RLS).

---

## Step 3 — Set Up Plane Cloud

1. Go to https://app.plane.so → Sign up / Sign in
2. Create a workspace (e.g. `ai-scrum-master`)
3. Create a project (e.g. `FinanceFlow`)
4. Create a **cycle** (Sprint 7 — label it clearly for demo)
5. Create at least 3 **issues** assigned to different members
6. Configure **states**: Backlog, In Progress, In Review, Done, Blocked

### Generate API Key

1. Go to Profile Settings → Personal Access Tokens
2. Click "Add personal access token"
3. Save the token — it starts with `plane_api_`

---

## Step 4 — Set Up n8n Cloud

n8n Cloud access will be provided at the event (track credits).

1. Log in at https://app.n8n.cloud
2. Create credentials for each service you'll connect:
   - **Google Gemini** — with your student API key
   - **Postgres** — your Supabase connection string
   - **HTTP Request** — for Plane API and GitHub API (no predefined credential needed)
3. Import the workflows from `n8n_workflows/` during the buildathon

---

## Step 5 — Set Up GitHub

1. Use a **single shared repository** for demo purposes
2. Generate a **Personal Access Token (classic)** with `repo` scope:
   - GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
   - Scopes: `repo` (full control)
3. Save the token for `.env.agent`

All three team members push commits to this repo during the demo sprint.

---

## Step 6 — Environment Variables

```bash
cp .env.agent.example .env.agent
```

Edit `.env.agent` with your real values:

| Variable | Where to Get It |
|---|---|
| `SUPABASE_URL` | Supabase → Project Settings → API → Project URL |
| `SUPABASE_ANON_KEY` | Supabase → Project Settings → API → `anon` public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Project Settings → API → `service_role` key (BACKEND ONLY) |
| `SUPABASE_DATABASE_URL` | Supabase → Project Settings → Database → Connection pooling (port 5432) |
| `PLANE_API_BASE_URL` | Use `https://api.plane.so/api/v1` |
| `PLANE_API_TOKEN` | Plane → Profile Settings → Personal Access Tokens |
| `PLANE_WORKSPACE_SLUG` | From your Plane workspace URL |
| `PLANE_PROJECT_ID` | From your Plane project URL (UUID after `/projects/`) |
| `GEMINI_API_KEY` | Google AI Studio (student credits) |
| `GEMINI_MODEL` | Set to `gemini-3.1-pro` or `gemini-3-flash` |
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `GITHUB_REPO` | Format: `owner/repo-name` |
| `AGENT_N8N_WEBHOOK_SECRET` | Generate: `openssl rand -hex 32` |
| `STANDUP_CRON` | Default: `45 8 * * 1-5` (weekdays at 8:45am) |
| `STANDUP_TIMEZONE` | e.g. `Asia/Colombo` |

Do **NOT** commit `.env.agent`. Confirm it is in `.gitignore`.

---

## Step 7 — Deploy Backend to Google Cloud Run

Lakindu owns this. Steps:

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/<project-id>/ai-scrum-master

# Deploy
gcloud run deploy ai-scrum-master \
  --image gcr.io/<project-id>/ai-scrum-master \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --env-vars-file .env.cloud.json
```

The backend URL will be something like `https://ai-scrum-master-xxxxx-uc.a.run.app`.

Update this URL in n8n's HTTP Request nodes.

---

## Step 8 — Final Verification Checklist

- [ ] `uv run uvicorn app.main:app` starts without errors
- [ ] Supabase tables exist and are accessible from the backend
- [ ] Plane API key works: `curl -H "X-API-Key: $KEY" https://api.plane.so/api/v1/workspaces/...`
- [ ] GitHub token works: `curl -H "Authorization: Bearer $TOKEN" https://api.github.com/user`
- [ ] `.env.agent` is populated and NOT in git
- [ ] Backend deploys to Cloud Run successfully
- [ ] n8n workflows are imported and credentials configured
- [ ] All three team members have push access to the shared repo

---

## Demo Script: FinanceFlow Sprint 7

**Product:** Mobile banking app "FinanceFlow"
**Sprint:** 7 (2 weeks, Day 3)

**Team:**
- Alice (Lakindu) — `feat/biometrics` — FaceID/TouchID login
- Bob (Stefan) — `fix/payment-timeout` — Payment retry with circuit breaker
- Carol (Saviskar) — `feat/dashboard` — Account summary dashboard

**Pre-seeded Plane data:**
- Sprint 7 cycle active
- 3 issues assigned (one per member), each in "In Progress"
- 1 blocker: Bob's CI test flakiness noted from Day 2

**Pre-seeded GitHub commits (last 24h):**
- Alice: `feat(biometrics): add FaceID enrollment flow` + `fix(biometrics): handle cancelled auth`
- Bob: `fix(payment-timeout): add circuit breaker` + `fix(payment-timeout): flaky test WIP`
- Carol: `feat(dashboard): transaction list component`

**Demo flow (2 mins):**
1. Show n8n workflow canvas (pre-fetch ran 45min ago) — 15s
2. Open Chat Trigger — standup begins — 10s
3. Agent asks Alice about FaceID commits — 20s
4. Alice responds, agent moves on — 10s
5. Agent asks Bob about circuit breaker + his blocker from yesterday — 20s
6. Bob responds, blocker updated — 10s
7. Agent asks Carol about dashboard component — 15s
8. Carol responds — 5s
9. Agent posts summary, writes to Plane cycle — 15s
10. Show Plane cycle description updated — 10s

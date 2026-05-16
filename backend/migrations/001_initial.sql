-- 001_initial.sql
-- Agentic Scrum Assistant — initial Supabase schema.
-- Run once in the Supabase SQL editor for a fresh project.
--
-- Notes:
--   - All tables are accessed by the backend via the Supabase service-role key
--     (RLS bypassed) and by n8n's Postgres node via SUPABASE_DATABASE_URL
--     (also bypasses RLS). RLS is intentionally NOT enabled for the MVP.
--   - UNIQUE constraints on standup_context and agent_memory are required for
--     idempotent upserts from the supabase-py SDK (`on_conflict=...`).
--   - `blockers.key` is the stable handle used by commit messages (e.g.
--     `[BLOCKER:bob-ci-flakiness]`) so n8n can update/resolve specific entries.

-- =============================================================================
-- participants
-- =============================================================================
CREATE TABLE IF NOT EXISTS participants (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plane_user_id   TEXT NOT NULL UNIQUE,
  display_name    TEXT NOT NULL,
  email           TEXT,
  github_login    TEXT,
  role            TEXT NOT NULL CHECK (role IN ('developer', 'ba', 'qa')),
  active          BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS participants_role_active_idx
  ON participants (role)
  WHERE active;

-- =============================================================================
-- standup_context
-- =============================================================================
CREATE TABLE IF NOT EXISTS standup_context (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sprint_id       TEXT NOT NULL,
  participant_id  TEXT NOT NULL,
  commits         JSONB NOT NULL DEFAULT '[]'::jsonb,
  blockers        JSONB NOT NULL DEFAULT '[]'::jsonb,
  last_summary    TEXT,
  compiled_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT standup_context_sprint_participant_uniq
    UNIQUE (sprint_id, participant_id)
);

CREATE INDEX IF NOT EXISTS standup_context_sprint_idx
  ON standup_context (sprint_id);

-- =============================================================================
-- agent_memory
-- =============================================================================
CREATE TABLE IF NOT EXISTS agent_memory (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  participant_id  TEXT NOT NULL,
  sprint_id       TEXT NOT NULL,
  standup_date    DATE NOT NULL,
  summary         TEXT NOT NULL,
  importance      INTEGER NOT NULL DEFAULT 1
                   CHECK (importance BETWEEN 1 AND 3),
  stale           BOOLEAN NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT agent_memory_participant_sprint_date_uniq
    UNIQUE (participant_id, sprint_id, standup_date)
);

CREATE INDEX IF NOT EXISTS agent_memory_sprint_stale_idx
  ON agent_memory (sprint_id, stale);

CREATE INDEX IF NOT EXISTS agent_memory_participant_sprint_idx
  ON agent_memory (participant_id, sprint_id);

-- =============================================================================
-- blockers
-- =============================================================================
CREATE TABLE IF NOT EXISTS blockers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key             TEXT NOT NULL UNIQUE,
  participant_id  TEXT NOT NULL,
  sprint_id       TEXT,
  description     TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'active'
                   CHECK (status IN ('active', 'resolved')),
  source          TEXT NOT NULL DEFAULT 'manual'
                   CHECK (source IN ('manual', 'github_commit', 'standup')),
  github_url      TEXT,
  last_update     TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS blockers_active_idx
  ON blockers (sprint_id, status)
  WHERE status = 'active';

CREATE INDEX IF NOT EXISTS blockers_participant_idx
  ON blockers (participant_id);

CREATE OR REPLACE FUNCTION touch_blockers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS blockers_touch_updated_at ON blockers;
CREATE TRIGGER blockers_touch_updated_at
  BEFORE UPDATE ON blockers
  FOR EACH ROW
  EXECUTE FUNCTION touch_blockers_updated_at();

-- =============================================================================
-- sprint_memory
-- =============================================================================
CREATE TABLE IF NOT EXISTS sprint_memory (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sprint_id       TEXT NOT NULL,
  key_fact        TEXT NOT NULL,
  category        TEXT NOT NULL
                   CHECK (category IN ('goal', 'decision', 'boundary', 'note')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS sprint_memory_sprint_category_idx
  ON sprint_memory (sprint_id, category);

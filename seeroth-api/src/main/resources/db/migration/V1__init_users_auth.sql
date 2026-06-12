-- ============================================================
-- V1: Users & Authentication
-- SeeRoth — Halal Investment Platform
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ── Mazhab enum ──────────────────────────────────────────────
CREATE TYPE mazhab_type AS ENUM (
    'SYAFII',
    'MALIKI', 
    'HANAFI',
    'HANBALI',
    'AAOIFI'
);

-- ── Risk tolerance enum ──────────────────────────────────────
CREATE TYPE risk_tolerance AS ENUM (
    'CONSERVATIVE',
    'MODERATE',
    'AGGRESSIVE'
);

-- ── Users ────────────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    
    -- Islamic profile
    mazhab          mazhab_type NOT NULL DEFAULT 'AAOIFI',
    risk_tolerance  risk_tolerance NOT NULL DEFAULT 'MODERATE',
    jurisdiction    VARCHAR(10) NOT NULL DEFAULT 'US',  -- ISO country code
    
    -- Simulation settings
    sim_capital     NUMERIC(15,2) NOT NULL DEFAULT 100000.00,
    
    -- Status
    is_active       BOOLEAN NOT NULL DEFAULT true,
    email_verified  BOOLEAN NOT NULL DEFAULT false,
    
    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Refresh tokens ────────────────────────────────────────────
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked     BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indexes ──────────────────────────────────────────────────
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);

-- ── Auto-update updated_at trigger ───────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

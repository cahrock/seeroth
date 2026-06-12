-- ============================================================
-- V2: Portfolio & Holdings
-- ============================================================

-- ── Halal status enum ────────────────────────────────────────
CREATE TYPE halal_status AS ENUM (
    'HALAL',
    'DOUBTFUL',
    'NOT_HALAL',
    'PENDING',
    'UNKNOWN'
);

-- ── Asset type enum ──────────────────────────────────────────
CREATE TYPE asset_type AS ENUM (
    'STOCK',
    'ETF',
    'SUKUK',
    'CASH'
);

-- ── Portfolios ────────────────────────────────────────────────
-- One user = one simulation portfolio (v1 MVP)
CREATE TABLE portfolios (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL DEFAULT 'My Halal Portfolio',
    
    -- Capital
    initial_capital NUMERIC(15,2) NOT NULL DEFAULT 100000.00,
    cash_balance    NUMERIC(15,2) NOT NULL DEFAULT 100000.00,
    
    -- Benchmark
    benchmark       VARCHAR(20) NOT NULL DEFAULT 'SPUS',
    
    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trigger_portfolios_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ── Holdings ─────────────────────────────────────────────────
CREATE TABLE holdings (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id        UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker              VARCHAR(20) NOT NULL,
    asset_type          asset_type NOT NULL DEFAULT 'STOCK',
    
    -- Position
    quantity            NUMERIC(15,6) NOT NULL DEFAULT 0,
    avg_cost_basis      NUMERIC(15,4) NOT NULL DEFAULT 0,
    
    -- Halal
    halal_status        halal_status NOT NULL DEFAULT 'PENDING',
    impure_income_ratio NUMERIC(6,4) NOT NULL DEFAULT 0,  -- e.g. 0.0137 = 1.37%
    
    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_portfolio_ticker UNIQUE (portfolio_id, ticker)
);

CREATE INDEX idx_holdings_portfolio_id ON holdings(portfolio_id);
CREATE INDEX idx_holdings_ticker ON holdings(ticker);

CREATE TRIGGER trigger_holdings_updated_at
    BEFORE UPDATE ON holdings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ── Transactions ──────────────────────────────────────────────
CREATE TYPE transaction_action AS ENUM (
    'BUY',
    'SELL',
    'DIVIDEND',
    'PURIFICATION',  -- Shariah purification payment
    'DEPOSIT',
    'WITHDRAWAL'
);

CREATE TABLE transactions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id    UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker          VARCHAR(20),  -- NULL for DEPOSIT/WITHDRAWAL
    action          transaction_action NOT NULL,
    
    -- Execution
    quantity        NUMERIC(15,6),
    price           NUMERIC(15,4),
    total_amount    NUMERIC(15,2) NOT NULL,
    commission      NUMERIC(10,4) NOT NULL DEFAULT 0,
    slippage        NUMERIC(10,4) NOT NULL DEFAULT 0,
    
    -- Signal context (for learning review)
    signal_score    SMALLINT,           -- L11 composite score at time of trade
    horizon_profile VARCHAR(30),        -- e.g. 'MONTHLY_INCOME'
    
    -- Purification
    purification_amount NUMERIC(15,4),
    
    -- Notes
    notes           TEXT,
    executed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_portfolio_id ON transactions(portfolio_id);
CREATE INDEX idx_transactions_ticker ON transactions(ticker);
CREATE INDEX idx_transactions_executed_at ON transactions(executed_at DESC);

-- ============================================================
-- V5: Zakat & Purification Records
-- ============================================================

-- ── Zakat calculation records ────────────────────────────────
CREATE TABLE zakat_records (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id        UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    
    -- Calculation metadata
    calculation_date    DATE NOT NULL,
    mazhab_used         mazhab_type NOT NULL,
    nisab_value_usd     NUMERIC(15,2) NOT NULL,  -- nisab threshold in USD at calc time
    
    -- Method A: Syafi'i/Maliki — 2.5% x Market Value
    method_a_base       NUMERIC(15,2),
    method_a_zakat      NUMERIC(15,2),
    
    -- Method B: AAOIFI — 2.5% x Zakatable Assets
    method_b_base       NUMERIC(15,2),
    method_b_zakat      NUMERIC(15,2),
    
    -- Method C: Hanafi — 2.5% x (Dividends + Realized Gains)
    method_c_base       NUMERIC(15,2),
    method_c_zakat      NUMERIC(15,2),
    
    -- Final amount (based on user's mazhab)
    recommended_zakat   NUMERIC(15,2) NOT NULL,
    
    -- Portfolio snapshot at calc time
    portfolio_value     NUMERIC(15,2) NOT NULL,
    
    -- Status
    is_paid             BOOLEAN NOT NULL DEFAULT false,
    paid_at             TIMESTAMPTZ,
    paid_amount         NUMERIC(15,2),
    notes               TEXT,
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_zakat_user_id ON zakat_records(user_id);
CREATE INDEX idx_zakat_date ON zakat_records(calculation_date DESC);

-- ── Purification records ──────────────────────────────────────
-- Tracks Shariah purification amounts per holding
CREATE TABLE purification_records (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id        UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker              VARCHAR(20) NOT NULL,
    
    -- Source of impurity
    source_type         VARCHAR(20) NOT NULL,  -- 'DIVIDEND' or 'CAPITAL_GAIN'
    gross_amount        NUMERIC(15,4) NOT NULL,
    impure_income_ratio NUMERIC(8,4) NOT NULL,
    purification_amount NUMERIC(15,4) NOT NULL, -- gross_amount * ratio
    
    -- Status
    is_paid             BOOLEAN NOT NULL DEFAULT false,
    paid_at             TIMESTAMPTZ,
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_purification_user_id ON purification_records(user_id);
CREATE INDEX idx_purification_ticker ON purification_records(ticker);

-- ── Behavioral journal ────────────────────────────────────────
-- L7 — captures Islamic reflection + trade psychology
CREATE TABLE behavioral_journal (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id  UUID REFERENCES transactions(id),  -- linked to a trade (optional)
    
    entry_type      VARCHAR(30) NOT NULL,  -- 'PRE_TRADE', 'POST_TRADE', 'MUHASABAH', 'REFLECTION'
    emotional_state VARCHAR(30),           -- 'CALM', 'FEARFUL', 'GREEDY', 'CONTENT'
    content         TEXT NOT NULL,
    
    -- Islamic reflection
    islamic_virtue  VARCHAR(30),           -- 'SABAR', 'TAWAKKUL', 'QANAAH', 'MUHASABAH'
    quran_ref       VARCHAR(50),           -- e.g. 'Al-Baqarah:2:275'
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_journal_user_id ON behavioral_journal(user_id);
CREATE INDEX idx_journal_created ON behavioral_journal(created_at DESC);

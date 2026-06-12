-- ============================================================
-- V3: Halal Screening Cache
-- Stores Zoya API results + AAOIFI ratio calculations
-- ============================================================

CREATE TABLE halal_screening_cache (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker                  VARCHAR(20) NOT NULL UNIQUE,
    exchange                VARCHAR(20),
    company_name            VARCHAR(255),
    
    -- L1: AAOIFI Standard 21 ratios
    halal_status            halal_status NOT NULL DEFAULT 'UNKNOWN',
    debt_to_market_cap      NUMERIC(8,4),   -- < 30% to pass
    interest_income_ratio   NUMERIC(8,4),   -- < 5% to pass
    cash_receivables_ratio  NUMERIC(8,4),   -- < 49% to pass
    
    -- Purification
    impure_income_ratio     NUMERIC(8,4) NOT NULL DEFAULT 0,
    
    -- Source
    source                  VARCHAR(50) NOT NULL DEFAULT 'ZOYA',
    source_rating           VARCHAR(20),     -- Zoya's own rating string
    
    -- Cache control
    screened_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until             TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '7 days',
    
    -- Timestamps
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_halal_cache_ticker ON halal_screening_cache(ticker);
CREATE INDEX idx_halal_cache_status ON halal_screening_cache(halal_status);
CREATE INDEX idx_halal_cache_valid_until ON halal_screening_cache(valid_until);

CREATE TRIGGER trigger_halal_cache_updated_at
    BEFORE UPDATE ON halal_screening_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ── Pre-seed known halal stocks (June 2026) ──────────────────
INSERT INTO halal_screening_cache 
    (ticker, company_name, halal_status, debt_to_market_cap, 
     interest_income_ratio, impure_income_ratio, source)
VALUES
    ('NVDA',  'NVIDIA Corporation',          'HALAL',    0.0137, 0.0080, 0.0137, 'MANUAL_SEED'),
    ('MSFT',  'Microsoft Corporation',       'HALAL',    0.0030, 0.0094, 0.0094, 'MANUAL_SEED'),
    ('META',  'Meta Platforms Inc',          'HALAL',    0.0320, 0.0106, 0.0106, 'MANUAL_SEED'),
    ('AMD',   'Advanced Micro Devices',      'HALAL',    0.0100, 0.0062, 0.0062, 'MANUAL_SEED'),
    ('AMAT',  'Applied Materials Inc',       'HALAL',    0.0180, 0.0050, 0.0050, 'MANUAL_SEED'),
    ('NVO',   'Novo Nordisk A/S',            'HALAL',    0.0250, 0.0030, 0.0030, 'MANUAL_SEED'),
    ('ISRG',  'Intuitive Surgical Inc',      'HALAL',    0.0050, 0.0020, 0.0020, 'MANUAL_SEED'),
    ('SPUS',  'SP Funds S&P 500 Sharia ETF', 'HALAL',    0.0000, 0.0000, 0.0000, 'MANUAL_SEED'),
    ('HLAL',  'Wahed FTSE USA Shariah ETF',  'HALAL',    0.0000, 0.0000, 0.0000, 'MANUAL_SEED'),
    ('UMMA',  'Wahed Dow Jones Islamic ETF', 'HALAL',    0.0000, 0.0000, 0.0000, 'MANUAL_SEED'),
    ('AAPL',  'Apple Inc',                   'DOUBTFUL', 0.0240, 0.0395, 0.0395, 'MANUAL_SEED'),
    ('JNJ',   'Johnson & Johnson',           'HALAL',    0.0190, 0.0040, 0.0040, 'MANUAL_SEED')
ON CONFLICT (ticker) DO UPDATE SET
    halal_status = EXCLUDED.halal_status,
    impure_income_ratio = EXCLUDED.impure_income_ratio,
    updated_at = NOW();

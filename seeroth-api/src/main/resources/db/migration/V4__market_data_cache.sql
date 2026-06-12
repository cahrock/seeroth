-- ============================================================
-- V4: Market Data Cache
-- Daily OHLCV + real-time price cache references
-- TimescaleDB hypertable for time-series efficiency
-- ============================================================

-- ── Daily OHLCV ───────────────────────────────────────────────
CREATE TABLE market_data_daily (
    time        TIMESTAMPTZ NOT NULL,
    ticker      VARCHAR(20) NOT NULL,
    open        NUMERIC(15,4) NOT NULL,
    high        NUMERIC(15,4) NOT NULL,
    low         NUMERIC(15,4) NOT NULL,
    close       NUMERIC(15,4) NOT NULL,
    volume      BIGINT NOT NULL,
    vwap        NUMERIC(15,4),
    source      VARCHAR(20) NOT NULL DEFAULT 'POLYGON',
    
    PRIMARY KEY (time, ticker)
);

-- Convert to TimescaleDB hypertable (partitioned by time)
SELECT create_hypertable('market_data_daily', 'time', if_not_exists => TRUE);

CREATE INDEX idx_market_daily_ticker_time 
    ON market_data_daily(ticker, time DESC);

-- ── Latest price snapshot ─────────────────────────────────────
-- Stores last known price for fast portfolio valuation
CREATE TABLE market_price_latest (
    ticker          VARCHAR(20) PRIMARY KEY,
    price           NUMERIC(15,4) NOT NULL,
    price_change    NUMERIC(10,4),      -- absolute change
    change_pct      NUMERIC(8,4),       -- % change
    volume          BIGINT,
    market_cap      NUMERIC(20,2),
    as_of           TIMESTAMPTZ NOT NULL,
    source          VARCHAR(20) NOT NULL DEFAULT 'POLYGON',
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_price_latest_updated ON market_price_latest(updated_at DESC);

-- ── Macro indicators cache ────────────────────────────────────
CREATE TABLE macro_indicators (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    series_id       VARCHAR(50) NOT NULL,   -- e.g. CPIAUCSL, DGS10
    series_name     VARCHAR(100) NOT NULL,
    value           NUMERIC(15,6) NOT NULL,
    observation_date DATE NOT NULL,
    source          VARCHAR(20) NOT NULL DEFAULT 'FRED',
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_series_date UNIQUE (series_id, observation_date)
);

CREATE INDEX idx_macro_series ON macro_indicators(series_id, observation_date DESC);

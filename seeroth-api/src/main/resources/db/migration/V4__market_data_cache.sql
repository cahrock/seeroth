-- ============================================================
-- V4: Market Data Cache (Plain PostgreSQL — no TimescaleDB)
-- TimescaleDB hypertable dapat ditambah di Phase 2 (AWS RDS)
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

CREATE INDEX idx_market_daily_ticker_time
    ON market_data_daily(ticker, time DESC);

-- ── Latest price snapshot ─────────────────────────────────────
CREATE TABLE market_price_latest (
    ticker          VARCHAR(20) PRIMARY KEY,
    price           NUMERIC(15,4) NOT NULL,
    price_change    NUMERIC(10,4),
    change_pct      NUMERIC(8,4),
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
    series_id       VARCHAR(50) NOT NULL,
    series_name     VARCHAR(100) NOT NULL,
    value           NUMERIC(15,6) NOT NULL,
    observation_date DATE NOT NULL,
    source          VARCHAR(20) NOT NULL DEFAULT 'FRED',
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_series_date UNIQUE (series_id, observation_date)
);

CREATE INDEX idx_macro_series ON macro_indicators(series_id, observation_date DESC);

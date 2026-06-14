"""
Pydantic schemas untuk Fundamental Data (L10 — FMP API)
Digunakan oleh L3 Stock Screening dan L11 Decision Engine
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class FundamentalScores(BaseModel):
    """
    Core fundamental metrics untuk L3 Stock Screening.
    Semua nilai dari FMP — SeeRoth portion hanya (bukan AAOIFI ratios).
    """
    ticker: str

    # ── Profitability ─────────────────────────────────────────
    gross_margin: Optional[float] = Field(None, description="Gross Profit / Revenue %")
    operating_margin: Optional[float] = Field(None, description="Operating Income / Revenue %")
    net_margin: Optional[float] = Field(None, description="Net Income / Revenue %")
    roe: Optional[float] = Field(None, description="Return on Equity %")
    roic: Optional[float] = Field(None, description="Return on Invested Capital %")

    # ── Growth ────────────────────────────────────────────────
    revenue_growth_1y: Optional[float] = Field(None, description="Revenue YoY growth % (1 year)")
    revenue_growth_3y: Optional[float] = Field(None, description="Revenue CAGR % (3 year)")
    eps_growth_1y: Optional[float] = Field(None, description="EPS YoY growth %")

    # ── Cash Flow ─────────────────────────────────────────────
    free_cash_flow: Optional[float] = Field(None, description="FCF in USD")
    fcf_margin: Optional[float] = Field(None, description="FCF / Revenue %")

    # ── Valuation ─────────────────────────────────────────────
    pe_ratio: Optional[float] = Field(None, description="Price / Earnings (TTM)")
    forward_pe: Optional[float] = Field(None, description="Forward P/E (1Y estimate)")
    p_fcf: Optional[float] = Field(None, description="Price / Free Cash Flow")
    ev_ebitda: Optional[float] = Field(None, description="Enterprise Value / EBITDA")
    peg_ratio: Optional[float] = Field(None, description="P/E to Growth ratio")
    price_to_book: Optional[float] = Field(None, description="Price / Book Value")

    # ── Analyst Estimates ─────────────────────────────────────
    eps_estimate_1y: Optional[float] = Field(None, description="EPS consensus estimate forward 1Y")
    eps_estimate_2y: Optional[float] = Field(None, description="EPS consensus estimate forward 2Y")
    revenue_estimate_1y: Optional[float] = Field(None, description="Revenue estimate forward 1Y")

    # ── Metadata ──────────────────────────────────────────────
    fiscal_year_end: Optional[str] = None
    currency: Optional[str] = "USD"
    fetched_at: Optional[datetime] = None
    source: str = "FMP"

    class Config:
        json_encoders = {datetime: str}


class EarningsEvent(BaseModel):
    """Single earnings announcement event."""
    ticker: str
    date: Optional[str] = None
    eps_estimated: Optional[float] = None
    eps_actual: Optional[float] = None
    revenue_estimated: Optional[float] = None
    revenue_actual: Optional[float] = None
    eps_surprise_pct: Optional[float] = None
    time: Optional[str] = None  # "bmo" (before market open) | "amc" (after market close)


class DividendRecord(BaseModel):
    """Single dividend payment record."""
    ticker: str
    date: Optional[str] = None
    record_date: Optional[str] = None
    payment_date: Optional[str] = None
    declaration_date: Optional[str] = None
    dividend: Optional[float] = None
    adj_dividend: Optional[float] = None


class FundamentalSummary(BaseModel):
    """
    Complete fundamental package untuk L3 scoring.
    Combines scores + earnings + dividend history.
    """
    ticker: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    scores: FundamentalScores
    next_earnings: Optional[EarningsEvent] = None
    last_dividend: Optional[DividendRecord] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

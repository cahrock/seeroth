"""
Pydantic schemas untuk Macro Indicators (L10 — FRED API)
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class MacroIndicator(BaseModel):
    """Single macro indicator data point."""
    series_id: str
    series_name: str
    value: float
    observation_date: date
    source: str = "FRED"
    fetched_at: datetime

    class Config:
        json_encoders = {date: str, datetime: str}


class MacroSnapshot(BaseModel):
    """Full macro snapshot — semua series sekaligus untuk L11 Decision Engine."""

    # Inflation
    cpi: Optional[float] = Field(None, description="CPI YoY % — CPIAUCSL")
    core_pce: Optional[float] = Field(None, description="Core PCE YoY % — PCEPILFE")

    # Labor Market
    nfp: Optional[float] = Field(None, description="Non-Farm Payrolls (thousands) — PAYEMS")
    unemployment_rate: Optional[float] = Field(None, description="Unemployment Rate % — UNRATE")
    jobless_claims: Optional[float] = Field(None, description="Initial Jobless Claims — ICSA")

    # Interest Rates & Yield Curve
    treasury_10y: Optional[float] = Field(None, description="10Y Treasury Yield % — DGS10")
    treasury_2y: Optional[float] = Field(None, description="2Y Treasury Yield % — DGS2")
    yield_curve: Optional[float] = Field(None, description="10Y-2Y Spread % — T10Y2Y")

    # Credit & Risk
    hy_credit_spread: Optional[float] = Field(None, description="HY Credit Spread % — BAMLH0A0HYM2")

    # Commodities
    wti_oil: Optional[float] = Field(None, description="WTI Crude Oil Price USD — DCOILWTICO")
    gold: Optional[float] = Field(None, description="Gold Price USD/troy oz — GOLDAMGBD228NLBM")

    # Metadata
    as_of: Optional[date] = None
    fetched_at: Optional[datetime] = None

    class Config:
        json_encoders = {date: str, datetime: str}


class MacroCycleAssessment(BaseModel):
    """
    L9 — 4-cycle macro assessment berdasarkan FRED data.
    Digunakan oleh L11 Decision Engine untuk weight adjustment.
    """
    cycle: str = Field(..., description="EXPANSION | PEAK | CONTRACTION | TROUGH")
    confidence: float = Field(..., ge=0, le=1, description="0.0 - 1.0")
    signals: dict = Field(default_factory=dict)
    snapshot: MacroSnapshot
    assessed_at: datetime

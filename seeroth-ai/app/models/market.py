"""
Pydantic schemas untuk Market Data (L10 — Polygon.io)
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class StockQuote(BaseModel):
    """Real-time/latest stock quote."""
    ticker: str
    price: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    prev_close: Optional[float] = None
    price_change: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    as_of: Optional[datetime] = None
    source: str = "POLYGON"

    class Config:
        json_encoders = {datetime: str}


class OHLCVBar(BaseModel):
    """Single OHLCV candlestick bar."""
    ticker: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None
    source: str = "POLYGON"

    class Config:
        json_encoders = {datetime: str}


class MarketStatus(BaseModel):
    """NYSE/NASDAQ market open/closed status."""
    market: str
    status: str                    # "open" | "closed" | "extended-hours"
    server_time: Optional[str] = None
    exchanges: Optional[dict] = None


class TickerDetails(BaseModel):
    """Company info from Polygon."""
    ticker: str
    name: Optional[str] = None
    market: Optional[str] = None
    locale: Optional[str] = None
    primary_exchange: Optional[str] = None
    type: Optional[str] = None
    currency_name: Optional[str] = None
    market_cap: Optional[float] = None
    share_class_shares_outstanding: Optional[float] = None
    description: Optional[str] = None
    homepage_url: Optional[str] = None
    list_date: Optional[str] = None

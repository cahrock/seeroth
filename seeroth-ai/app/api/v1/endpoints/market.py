"""
L10 Data Feed — Market Data API Endpoints (Polygon.io)

GET /api/v1/market/status              — Market open/closed status
GET /api/v1/market/quote/{ticker}      — Latest stock price
GET /api/v1/market/quotes              — Multiple tickers at once
GET /api/v1/market/history/{ticker}    — Historical OHLCV bars
GET /api/v1/market/details/{ticker}    — Company info
"""

import logging
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.market import StockQuote, OHLCVBar, MarketStatus, TickerDetails
from app.services.market.polygon_client import polygon_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/status", response_model=MarketStatus, summary="Market open/closed status")
async def get_market_status():
    """Check apakah NYSE/NASDAQ sedang open atau closed."""
    return await polygon_client.get_market_status()


@router.get("/quote/{ticker}", response_model=StockQuote, summary="Latest stock price")
async def get_stock_quote(ticker: str):
    """
    Get latest stock price untuk satu ticker.
    Returns previous day OHLCV + price change.

    Example: /api/v1/market/quote/NVDA
    """
    quote = await polygon_client.get_stock_quote(ticker.upper())
    if not quote:
        raise HTTPException(
            status_code=404,
            detail=f"No price data available for {ticker.upper()}"
        )
    return quote


@router.get("/quotes", summary="Multiple stock quotes")
async def get_multiple_quotes(
    tickers: str = Query(..., description="Comma-separated tickers, e.g. NVDA,MSFT,META")
):
    """
    Get latest prices untuk multiple tickers sekaligus.
    Digunakan untuk portfolio valuation di dashboard.

    Example: /api/v1/market/quotes?tickers=NVDA,MSFT,META,SPUS
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    if not ticker_list:
        raise HTTPException(status_code=400, detail="No tickers provided")
    if len(ticker_list) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 tickers per request")

    results = await polygon_client.get_multiple_quotes(ticker_list)

    return {
        "requested": len(ticker_list),
        "returned": len(results),
        "quotes": {ticker: quote.model_dump() for ticker, quote in results.items()}
    }


@router.get("/history/{ticker}", response_model=List[OHLCVBar], summary="Historical OHLCV")
async def get_historical_bars(
    ticker: str,
    days: int = Query(default=30, ge=1, le=365, description="Number of days of history"),
    timespan: str = Query(default="day", description="Bar timespan: day | week | month"),
):
    """
    Get historical OHLCV bars untuk charting (L4 Technical Analysis).

    Example: /api/v1/market/history/NVDA?days=90&timespan=day
    """
    if timespan not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="timespan must be: day, week, or month")

    to_date = date.today()
    from_date = to_date - timedelta(days=days)

    bars = await polygon_client.get_historical_bars(
        ticker.upper(), from_date, to_date, timespan
    )

    if not bars:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data for {ticker.upper()}"
        )

    return bars


@router.get("/details/{ticker}", response_model=TickerDetails, summary="Company details")
async def get_ticker_details(ticker: str):
    """
    Get company info — name, market cap, exchange, description.
    Digunakan oleh L3 Stock Screening.

    Example: /api/v1/market/details/NVDA
    """
    details = await polygon_client.get_ticker_details(ticker.upper())
    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"No details found for {ticker.upper()}"
        )
    return details

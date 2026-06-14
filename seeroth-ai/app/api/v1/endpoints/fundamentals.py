"""
L10 Data Feed — Fundamentals API Endpoints (FMP)

GET /api/v1/fundamentals/scores/{ticker}    — Core fundamental metrics
GET /api/v1/fundamentals/summary/{ticker}   — Full package (scores + earnings + dividends)
GET /api/v1/fundamentals/earnings/calendar  — Upcoming earnings dates
GET /api/v1/fundamentals/dividends/{ticker} — Dividend history
"""

import logging
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.fundamentals import FundamentalScores, FundamentalSummary, EarningsEvent
from app.services.fundamentals.fmp_client import fmp_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/scores/{ticker}",
    response_model=FundamentalScores,
    summary="Core fundamental scores (L3 Stock Screening)"
)
async def get_fundamental_scores(ticker: str):
    """
    Fetch core fundamental metrics untuk L3 Stock Screening.

    Returns: margins, ROIC, FCF, valuation ratios, growth rates, EPS estimates.

    Example: /api/v1/fundamentals/scores/NVDA
    """
    scores = await fmp_client.get_fundamental_scores(ticker.upper())
    if not scores:
        raise HTTPException(
            status_code=404,
            detail=f"No fundamental data available for {ticker.upper()}"
        )
    return scores


@router.get(
    "/summary/{ticker}",
    response_model=FundamentalSummary,
    summary="Complete fundamental package"
)
async def get_fundamental_summary(ticker: str):
    """
    Complete fundamental package — scores + last earnings + dividend history.
    One-stop endpoint untuk L3 Stock Screening dashboard card.

    Example: /api/v1/fundamentals/summary/NVDA
    """
    summary = await fmp_client.get_fundamental_summary(ticker.upper())
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"No fundamental data available for {ticker.upper()}"
        )
    return summary


@router.get(
    "/earnings/calendar",
    summary="Upcoming earnings calendar (L11 Decision Engine)"
)
async def get_earnings_calendar(
    days_ahead: int = Query(default=30, ge=1, le=90, description="Days ahead to look")
):
    """
    Fetch upcoming earnings announcement dates.
    Digunakan oleh L11 Decision Engine untuk timing signals —
    hindari entry 3 hari sebelum earnings.

    Example: /api/v1/fundamentals/earnings/calendar?days_ahead=14
    """
    from_date = date.today()
    to_date = from_date + timedelta(days=days_ahead)

    calendar = await fmp_client.get_earnings_calendar(from_date, to_date)
    if calendar is None:
        raise HTTPException(status_code=503, detail="FMP earnings calendar unavailable")

    return {
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "count": len(calendar),
        "events": calendar
    }


@router.get(
    "/dividends/{ticker}",
    summary="Dividend history"
)
async def get_dividend_history(ticker: str):
    """
    Fetch dividend payment history.
    Digunakan oleh L6 Zakat & Purification calculator
    untuk menghitung dividend purification amount.

    Example: /api/v1/fundamentals/dividends/MSFT
    """
    dividends = await fmp_client.get_dividend_history(ticker.upper())
    if dividends is None:
        raise HTTPException(
            status_code=404,
            detail=f"No dividend history for {ticker.upper()}"
        )

    return {
        "ticker": ticker.upper(),
        "count": len(dividends),
        "dividends": dividends
    }

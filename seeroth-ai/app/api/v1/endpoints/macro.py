"""
L10 Data Feed — Macro Indicators API Endpoints
GET /api/v1/macro/snapshot    — Full macro snapshot (semua 11 series)
GET /api/v1/macro/series/{id} — Single FRED series latest value
GET /api/v1/macro/cycle       — Current macro cycle assessment (L9)
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.macro import MacroSnapshot, MacroCycleAssessment
from app.services.macro.fred_client import fred_client, FRED_SERIES

logger = logging.getLogger(__name__)
router = APIRouter()


class SeriesResponse(BaseModel):
    series_id: str
    series_name: str
    value: float
    observation_date: str
    source: str = "FRED"


@router.get("/snapshot", response_model=MacroSnapshot, summary="Full macro snapshot")
async def get_macro_snapshot():
    """
    Fetch semua 11 FRED macro indicators sekaligus.
    Digunakan oleh L11 Decision Engine dan L12 AI Advisory.

    Cache: Redis 15 menit (TODO: inject redis_client di Phase 2)
    """
    try:
        snapshot = await fred_client.fetch_macro_snapshot()
        return snapshot
    except Exception as e:
        logger.error(f"Macro snapshot error: {e}")
        raise HTTPException(status_code=503, detail=f"FRED API unavailable: {str(e)}")


@router.get("/series/{series_key}", response_model=SeriesResponse, summary="Single FRED series")
async def get_single_series(series_key: str):
    """
    Fetch satu FRED series berdasarkan key.

    Available keys: cpi, core_pce, nfp, unemployment_rate, jobless_claims,
    treasury_10y, treasury_2y, yield_curve, hy_credit_spread, wti_oil, gold
    """
    if series_key not in FRED_SERIES:
        valid_keys = list(FRED_SERIES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unknown series key '{series_key}'. Valid keys: {valid_keys}"
        )

    series_id, series_name = FRED_SERIES[series_key]
    indicator = await fred_client.fetch_series_latest(series_id, series_name)

    if not indicator:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch FRED series {series_id}"
        )

    return SeriesResponse(
        series_id=indicator.series_id,
        series_name=indicator.series_name,
        value=indicator.value,
        observation_date=str(indicator.observation_date),
    )


@router.get("/cycle", response_model=MacroCycleAssessment, summary="Macro cycle assessment (L9)")
async def get_macro_cycle():
    """
    L9 — Assess current macro cycle berdasarkan FRED data.
    Returns: EXPANSION | PEAK | CONTRACTION | TROUGH

    Digunakan oleh L11 Decision Engine untuk weight adjustment
    pada semua 5 trading horizon profiles.
    """
    try:
        snapshot = await fred_client.fetch_macro_snapshot()
        cycle = await fred_client.assess_macro_cycle(snapshot)

        # Build signals summary
        signals = {}
        if snapshot.yield_curve is not None:
            signals["yield_curve"] = f"{snapshot.yield_curve:.2f}% ({'normal' if snapshot.yield_curve > 0 else 'INVERTED'})"
        if snapshot.cpi is not None:
            signals["cpi"] = f"{snapshot.cpi:.1f}% ({'elevated' if snapshot.cpi > 4 else 'moderate'})"
        if snapshot.unemployment_rate is not None:
            signals["unemployment"] = f"{snapshot.unemployment_rate:.1f}%"
        if snapshot.hy_credit_spread is not None:
            signals["credit_spread"] = f"{snapshot.hy_credit_spread:.2f}% ({'wide' if snapshot.hy_credit_spread > 5 else 'tight'})"

        # Simple confidence scoring
        confidence_map = {"EXPANSION": 0.75, "PEAK": 0.65, "CONTRACTION": 0.80, "TROUGH": 0.60, "UNKNOWN": 0.0}

        return MacroCycleAssessment(
            cycle=cycle,
            confidence=confidence_map.get(cycle, 0.5),
            signals=signals,
            snapshot=snapshot,
            assessed_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Macro cycle error: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/series-list", summary="List all available FRED series")
async def list_series():
    """List semua FRED series yang di-track oleh SeeRoth."""
    return {
        key: {"series_id": sid, "name": name}
        for key, (sid, name) in FRED_SERIES.items()
    }

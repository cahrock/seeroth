"""
L10 Data Feed — FRED API Client
"""

import logging
from datetime import date, datetime
from typing import Optional

import httpx

from app.core.config import settings
from app.models.macro import MacroIndicator, MacroSnapshot

logger = logging.getLogger(__name__)

FRED_BASE_URL = "https://api.stlouisfed.org/fred"

FRED_SERIES = {
    "cpi":               ("CPIAUCSL",          "CPI All Urban Consumers"),
    "core_pce":          ("PCEPILFE",           "Core PCE Price Index"),
    "nfp":               ("PAYEMS",             "Non-Farm Payrolls"),
    "unemployment_rate": ("UNRATE",             "Unemployment Rate"),
    "jobless_claims":    ("ICSA",               "Initial Jobless Claims"),
    "treasury_10y":      ("DGS10",              "10-Year Treasury Yield"),
    "treasury_2y":       ("DGS2",               "2-Year Treasury Yield"),
    "yield_curve":       ("T10Y2Y",             "10Y-2Y Yield Curve Spread"),
    "hy_credit_spread":  ("BAMLH0A0HYM2",       "HY Credit Spread"),
    "wti_oil":           ("DCOILWTICO",          "WTI Crude Oil Price"),
    "gold":              ("GOLDAMGBD228NLBM",    "Gold Price USD"),
}


class FredClient:
    """
    Async FRED API client.
    Menggunakan fresh AsyncClient per request untuk menghindari
    connection state issues di development.
    """

    def __init__(self):
        self.api_key = settings.fred_api_key
        self.base_url = FRED_BASE_URL

    async def fetch_series_latest(self, series_id: str, series_name: str) -> Optional[MacroIndicator]:
        """Fetch nilai terbaru dari satu FRED series."""
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 5,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/series/observations",
                    params=params
                )
                response.raise_for_status()
                data = response.json()

            observations = data.get("observations", [])
            for obs in observations:
                value_str = obs.get("value", ".")
                if value_str != ".":
                    return MacroIndicator(
                        series_id=series_id,
                        series_name=series_name,
                        value=float(value_str),
                        observation_date=date.fromisoformat(obs["date"]),
                        source="FRED",
                        fetched_at=datetime.utcnow(),
                    )

            logger.warning(f"No valid observations for FRED series {series_id}")
            return None

        except httpx.HTTPStatusError as e:
            logger.error(f"FRED HTTP error {series_id}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"FRED error {series_id}: {e}")
            return None

    async def fetch_macro_snapshot(self) -> MacroSnapshot:
        """Fetch semua 11 series dan return MacroSnapshot."""
        logger.info("Fetching full macro snapshot from FRED...")

        snapshot_data = {}
        fetch_errors = []

        for field_name, (series_id, series_name) in FRED_SERIES.items():
            indicator = await self.fetch_series_latest(series_id, series_name)
            if indicator:
                snapshot_data[field_name] = indicator.value
                logger.info(f"  {series_id}: {indicator.value} ({indicator.observation_date})")
            else:
                fetch_errors.append(series_id)
                snapshot_data[field_name] = None

        if fetch_errors:
            logger.warning(f"Failed to fetch: {fetch_errors}")

        return MacroSnapshot(
            **snapshot_data,
            as_of=date.today(),
            fetched_at=datetime.utcnow(),
        )

    async def assess_macro_cycle(self, snapshot: MacroSnapshot) -> str:
        """L9 — Rule-based macro cycle assessment."""
        if not snapshot.yield_curve or not snapshot.cpi:
            return "UNKNOWN"

        yield_curve = snapshot.yield_curve
        cpi = snapshot.cpi
        credit_spread = snapshot.hy_credit_spread or 4.0
        unemployment = snapshot.unemployment_rate or 4.5

        if yield_curve > 0.5 and cpi < 4.0 and unemployment < 5.0:
            return "EXPANSION"
        elif yield_curve < 0 and credit_spread > 5.0:
            return "CONTRACTION"
        elif cpi > 4.0 and yield_curve < 0.5:
            return "PEAK"
        else:
            return "TROUGH"

    async def close(self):
        pass  # No persistent client to close


# Singleton instance
fred_client = FredClient()

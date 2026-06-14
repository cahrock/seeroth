"""
L10 Data Feed — Financial Modeling Prep (FMP) Client
Base URL: https://financialmodelingprep.com/stable/

IMPORTANT: FMP stable API requires URL-embedded parameters.
httpx params={} dict causes parameter encoding issues.
Solution: Build complete URL strings directly.

SeeRoth fetches (Opsi D — skeleton v3):
  - Income statement    → revenue, gross profit, operating income
  - Cash flow           → free cash flow
  - Ratios              → P/E, P/FCF, EV/EBITDA, PEG, margins, ROIC
  - Key metrics         → FCF, market cap, enterprise value
  - Ratios TTM          → trailing twelve months ratios
  - Key metrics TTM     → trailing twelve months metrics
  - Analyst estimates   → EPS forward 1Y, 2Y
  - Earnings            → upcoming earnings dates + EPS estimates
  - Dividends           → dividend history
  - Financial growth    → revenue growth YoY
  - Profile             → company info, sector, market cap

NOTE: AAOIFI ratios (debt, interest income, assets) = BaQool domain.
This client does NOT fetch those ratios.
"""

import logging
from datetime import date, datetime
from typing import Optional, List

import httpx

from app.core.config import settings
from app.models.fundamentals import (
    FundamentalScores,
    EarningsEvent,
    DividendRecord,
    FundamentalSummary,
)

logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/stable"


class FmpClient:
    """
    Async FMP stable API client.
    
    Key pattern: URL parameters embedded directly in URL string.
    Do NOT use httpx params={} — causes symbol parameter encoding issues.
    """

    def __init__(self):
        self.api_key = settings.fmp_api_key
        self.base_url = FMP_BASE_URL

    def _url(self, endpoint: str, symbol: str = None, extra: str = "") -> str:
        """Build complete FMP URL with embedded parameters."""
        if symbol:
            return f"{self.base_url}/{endpoint}?symbol={symbol}&apikey={self.api_key}{extra}"
        return f"{self.base_url}/{endpoint}?apikey={self.api_key}{extra}"

    async def _get(self, url: str) -> Optional[list | dict]:
        """Generic GET with pre-built URL."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(url)
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"FMP HTTP error: {e.response.status_code} — {url}")
            return None
        except Exception as e:
            logger.error(f"FMP error: {e} — {url}")
            return None

    async def get_ratios(self, ticker: str) -> Optional[dict]:
        """Annual financial ratios — P/E, margins, ROIC, ROE."""
        url = self._url("ratios", ticker, "&limit=1")
        data = await self._get(url)
        return data[0] if data and isinstance(data, list) else None

    async def get_ratios_ttm(self, ticker: str) -> Optional[dict]:
        """Trailing twelve months ratios — more current than annual."""
        url = self._url("ratios-ttm", ticker)
        data = await self._get(url)
        return data[0] if data and isinstance(data, list) else None

    async def get_key_metrics(self, ticker: str) -> Optional[dict]:
        """Key metrics — market cap, enterprise value, FCF."""
        url = self._url("key-metrics", ticker, "&limit=1")
        data = await self._get(url)
        return data[0] if data and isinstance(data, list) else None

    async def get_key_metrics_ttm(self, ticker: str) -> Optional[dict]:
        """Trailing twelve months key metrics."""
        url = self._url("key-metrics-ttm", ticker)
        data = await self._get(url)
        return data[0] if data and isinstance(data, list) else None

    async def get_income_statement(self, ticker: str) -> Optional[dict]:
        """Latest 2 annual income statements for YoY growth calculation."""
        url = self._url("income-statement", ticker, "&limit=2")
        data = await self._get(url)
        if data and isinstance(data, list):
            if len(data) >= 2:
                return {"latest": data[0], "prior": data[1]}
            elif len(data) == 1:
                return {"latest": data[0], "prior": None}
        return None

    async def get_cash_flow(self, ticker: str) -> Optional[dict]:
        """Latest cash flow statement — operating CF, capex, FCF."""
        url = self._url("cash-flow-statement", ticker, "&limit=1")
        data = await self._get(url)
        return data[0] if data and isinstance(data, list) else None

    async def get_financial_growth(self, ticker: str) -> Optional[dict]:
        """Financial growth rates — revenue, earnings, FCF growth."""
        url = self._url("financial-growth", ticker, "&limit=1")
        data = await self._get(url)
        return data[0] if data and isinstance(data, list) else None

    async def get_analyst_estimates(self, ticker: str) -> Optional[list]:
        """Analyst EPS and revenue estimates — forward 1Y and 2Y."""
        url = self._url("analyst-estimates", ticker, "&period=annual&limit=2")
        data = await self._get(url)
        return data if data and isinstance(data, list) else None

    async def get_earnings(self, ticker: str) -> Optional[list]:
        """Upcoming and recent earnings dates + EPS estimates."""
        url = self._url("earnings", ticker)
        data = await self._get(url)
        return data[:4] if data and isinstance(data, list) else None

    async def get_earnings_calendar(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Optional[list]:
        """Upcoming earnings calendar — all companies."""
        extra = ""
        if from_date:
            extra += f"&from={from_date.isoformat()}"
        if to_date:
            extra += f"&to={to_date.isoformat()}"
        url = self._url("earnings-calendar", extra=extra)
        return await self._get(url)

    async def get_dividend_history(self, ticker: str) -> Optional[list]:
        """Dividend payment history — untuk purification calculation."""
        url = self._url("dividends", ticker)
        data = await self._get(url)
        return data[:8] if data and isinstance(data, list) else None

    async def get_profile(self, ticker: str) -> Optional[dict]:
        """Company profile — name, sector, exchange, market cap."""
        url = self._url("profile", ticker)
        data = await self._get(url)
        return data[0] if data and isinstance(data, list) else None

    async def get_fundamental_scores(self, ticker: str) -> Optional[FundamentalScores]:
        """
        Main method — aggregates FMP data menjadi FundamentalScores.
        Dipanggil oleh L3 Stock Screening engine.
        Menggunakan TTM (trailing twelve months) untuk data terkini.
        """
        ticker = ticker.upper()
        logger.info(f"Fetching fundamental scores for {ticker}...")

        # Fetch data — TTM lebih current dari annual
        ratios_ttm = await self.get_ratios_ttm(ticker)
        metrics_ttm = await self.get_key_metrics_ttm(ticker)
        growth = await self.get_financial_growth(ticker)
        cash_flow = await self.get_cash_flow(ticker)
        estimates = await self.get_analyst_estimates(ticker)

        if not ratios_ttm and not metrics_ttm:
            logger.warning(f"No fundamental data for {ticker}")
            return None

        # ── Revenue growth dari financial-growth endpoint ─────
        revenue_growth_1y = None
        if growth:
            rev_growth = growth.get("revenueGrowth")
            if rev_growth is not None:
                revenue_growth_1y = rev_growth * 100  # convert to %

        # ── FCF dari cash flow statement ──────────────────────
        fcf = None
        fcf_margin = None
        if cash_flow:
            fcf = cash_flow.get("freeCashFlow")
            revenue = cash_flow.get("netIncome")  # fallback
            # Try to get revenue from cash flow context
            operating_cf = cash_flow.get("operatingCashFlow")
            capex = cash_flow.get("capitalExpenditure", 0)
            if operating_cf and capex is not None:
                fcf = operating_cf - abs(capex)

        # ── EPS estimates ─────────────────────────────────────
        eps_1y = eps_2y = rev_est_1y = None
        if estimates and len(estimates) >= 1:
            eps_1y = estimates[0].get("epsAvg") or estimates[0].get("epsEstimated")
            rev_est_1y = estimates[0].get("revenueAvg")
        if estimates and len(estimates) >= 2:
            eps_2y = estimates[1].get("epsAvg") or estimates[1].get("epsEstimated")

        return FundamentalScores(
            ticker=ticker,

            # Profitability (TTM — most current)
            gross_margin=(ratios_ttm.get("grossProfitMarginTTM") or 0) * 100 if ratios_ttm else None,
            operating_margin=(ratios_ttm.get("operatingProfitMarginTTM") or 0) * 100 if ratios_ttm else None,
            net_margin=(ratios_ttm.get("netProfitMarginTTM") or 0) * 100 if ratios_ttm else None,
            roe=(ratios_ttm.get("returnOnEquityTTM") or 0) * 100 if ratios_ttm else None,
            roic=(ratios_ttm.get("returnOnCapitalEmployedTTM") or 0) * 100 if ratios_ttm else None,

            # Growth
            revenue_growth_1y=revenue_growth_1y,

            # Cash Flow
            free_cash_flow=fcf,

            # Valuation (TTM)
            pe_ratio=ratios_ttm.get("peRatioTTM") if ratios_ttm else None,
            p_fcf=ratios_ttm.get("priceToFreeCashFlowsRatioTTM") if ratios_ttm else None,
            ev_ebitda=ratios_ttm.get("enterpriseValueMultipleTTM") if ratios_ttm else None,
            peg_ratio=ratios_ttm.get("pegRatioTTM") if ratios_ttm else None,
            price_to_book=ratios_ttm.get("priceToBookRatioTTM") if ratios_ttm else None,

            # Estimates
            eps_estimate_1y=eps_1y,
            eps_estimate_2y=eps_2y,
            revenue_estimate_1y=rev_est_1y,

            fetched_at=datetime.utcnow(),
            source="FMP",
        )

    async def get_fundamental_summary(self, ticker: str) -> Optional[FundamentalSummary]:
        """
        Complete fundamental package — scores + earnings + dividends.
        One-stop call untuk L3 Stock Screening dashboard.
        """
        ticker = ticker.upper()

        scores = await self.get_fundamental_scores(ticker)
        if not scores:
            return None

        profile = await self.get_profile(ticker)

        # Next earnings event
        next_earnings = None
        earnings_data = await self.get_earnings(ticker)
        if earnings_data and len(earnings_data) > 0:
            e = earnings_data[0]
            next_earnings = EarningsEvent(
                ticker=ticker,
                date=e.get("date"),
                eps_estimated=e.get("epsEstimated"),
                eps_actual=e.get("epsActual"),
                revenue_estimated=e.get("revenueEstimated"),
                revenue_actual=e.get("revenueActual"),
            )

        # Last dividend
        last_dividend = None
        dividends = await self.get_dividend_history(ticker)
        if dividends and len(dividends) > 0:
            d = dividends[0]
            last_dividend = DividendRecord(
                ticker=ticker,
                date=d.get("date"),
                payment_date=d.get("paymentDate"),
                dividend=d.get("dividend"),
                adj_dividend=d.get("adjDividend"),
            )

        return FundamentalSummary(
            ticker=ticker,
            company_name=profile.get("companyName") if profile else None,
            sector=profile.get("sector") if profile else None,
            industry=profile.get("industry") if profile else None,
            scores=scores,
            next_earnings=next_earnings,
            last_dividend=last_dividend,
        )


# Singleton instance
fmp_client = FmpClient()

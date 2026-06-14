"""
Unit tests untuk L10 FMP Client
Tests menggunakan mock — tidak perlu real API key
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.fundamentals import FundamentalScores
from app.services.fundamentals.fmp_client import FmpClient


@pytest.fixture
def fmp_client():
    return FmpClient()


@pytest.fixture
def mock_ratios():
    return [{
        "grossProfitMargin": 0.7245,
        "operatingProfitMargin": 0.6124,
        "netProfitMargin": 0.5561,
        "returnOnEquity": 1.2345,
        "returnOnCapitalEmployed": 0.4521,
        "priceEarningsRatio": 35.2,
        "priceToFreeCashFlowsRatio": 42.1,
        "enterpriseValueMultiple": 28.5,
        "priceEarningsToGrowthRatio": 1.8,
        "priceToBookRatio": 22.4,
        "earningsPerShareGrowth": 0.1234,
    }]


@pytest.fixture
def mock_income():
    return [
        {"revenue": 130000000000, "grossProfit": 94000000000},
        {"revenue": 107000000000, "grossProfit": 77000000000},
    ]


@pytest.fixture
def mock_cash_flow():
    return [{"freeCashFlow": 55000000000}]


@pytest.fixture
def mock_estimates():
    return [
        {"estimatedEpsAvg": 3.45, "estimatedRevenueAvg": 150000000000},
        {"estimatedEpsAvg": 4.12, "estimatedRevenueAvg": 175000000000},
    ]


class TestFmpClientFetch:

    @pytest.mark.asyncio
    async def test_get_fundamental_scores_success(
        self, fmp_client, mock_ratios, mock_income, mock_cash_flow, mock_estimates
    ):
        async def mock_get(endpoint, params=None):
            if "ratios" in endpoint:
                return mock_ratios
            elif "income-statement" in endpoint:
                return mock_income
            elif "cash-flow" in endpoint:
                return mock_cash_flow
            elif "analyst-estimates" in endpoint:
                return mock_estimates
            elif "key-metrics" in endpoint:
                return [{"freeCashFlow": 55000000000}]
            return None

        fmp_client._get = mock_get

        scores = await fmp_client.get_fundamental_scores("NVDA")

        assert scores is not None
        assert scores.ticker == "NVDA"
        assert scores.gross_margin == pytest.approx(72.45, 0.01)
        assert scores.pe_ratio == 35.2
        assert scores.ev_ebitda == 28.5
        assert scores.eps_estimate_1y == 3.45
        assert scores.eps_estimate_2y == 4.12
        assert scores.source == "FMP"

    @pytest.mark.asyncio
    async def test_revenue_growth_calculated_correctly(
        self, fmp_client, mock_ratios, mock_cash_flow, mock_estimates
    ):
        """Revenue growth = (latest - prior) / prior * 100"""
        async def mock_get(endpoint, params=None):
            if "ratios" in endpoint:
                return mock_ratios
            elif "income-statement" in endpoint:
                # latest: 130B, prior: 107B → growth = 21.5%
                return [
                    {"revenue": 130000000000},
                    {"revenue": 107000000000},
                ]
            elif "cash-flow" in endpoint:
                return mock_cash_flow
            elif "analyst-estimates" in endpoint:
                return mock_estimates
            elif "key-metrics" in endpoint:
                return [{}]
            return None

        fmp_client._get = mock_get
        scores = await fmp_client.get_fundamental_scores("NVDA")

        assert scores is not None
        expected_growth = ((130 - 107) / 107) * 100
        assert scores.revenue_growth_1y == pytest.approx(expected_growth, 0.01)

    @pytest.mark.asyncio
    async def test_get_scores_returns_none_when_no_data(self, fmp_client):
        async def mock_get(endpoint, params=None):
            return None

        fmp_client._get = mock_get
        scores = await fmp_client.get_fundamental_scores("INVALID")
        assert scores is None

    @pytest.mark.asyncio
    async def test_ticker_always_uppercase(self, fmp_client, mock_ratios, mock_income, mock_cash_flow, mock_estimates):
        async def mock_get(endpoint, params=None):
            if "ratios" in endpoint:
                return mock_ratios
            elif "income-statement" in endpoint:
                return mock_income
            elif "cash-flow" in endpoint:
                return mock_cash_flow
            elif "analyst-estimates" in endpoint:
                return mock_estimates
            elif "key-metrics" in endpoint:
                return [{}]
            return None

        fmp_client._get = mock_get
        scores = await fmp_client.get_fundamental_scores("nvda")  # lowercase

        assert scores is not None
        assert scores.ticker == "NVDA"  # should be uppercase


class TestFmpEarningsCalendar:

    @pytest.mark.asyncio
    async def test_earnings_calendar_returns_list(self, fmp_client):
        mock_events = [
            {"symbol": "NVDA", "date": "2026-08-28", "epsEstimated": 0.85},
            {"symbol": "MSFT", "date": "2026-07-30", "epsEstimated": 3.10},
        ]

        async def mock_get(endpoint, params=None):
            return mock_events

        fmp_client._get = mock_get
        from datetime import date
        result = await fmp_client.get_earnings_calendar(date.today())
        assert result is not None
        assert len(result) == 2

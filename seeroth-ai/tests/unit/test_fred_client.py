"""
Unit tests untuk L10 FRED Client
Tests menggunakan mock — tidak perlu real API key
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.macro import MacroIndicator, MacroSnapshot
from app.services.macro.fred_client import FredClient, FRED_SERIES


@pytest.fixture
def fred_client():
    return FredClient()


@pytest.fixture
def mock_fred_response():
    """Mock response dari FRED API."""
    return {
        "observations": [
            {"date": "2026-06-01", "value": "3.4"},
            {"date": "2026-05-01", "value": "3.5"},
        ]
    }


@pytest.fixture
def mock_fred_missing_response():
    """Mock response dengan missing value (dot notation)."""
    return {
        "observations": [
            {"date": "2026-06-01", "value": "."},
            {"date": "2026-05-01", "value": "3.5"},
        ]
    }


class TestFredSeriesConfig:
    """Test FRED series configuration."""

    def test_all_required_series_present(self):
        required = [
            "cpi", "core_pce", "nfp", "unemployment_rate",
            "jobless_claims", "treasury_10y", "treasury_2y",
            "yield_curve", "hy_credit_spread", "wti_oil", "gold"
        ]
        for key in required:
            assert key in FRED_SERIES, f"Missing required series: {key}"

    def test_series_have_id_and_name(self):
        for key, (series_id, name) in FRED_SERIES.items():
            assert series_id, f"Empty series_id for {key}"
            assert name, f"Empty name for {key}"

    def test_correct_series_ids(self):
        assert FRED_SERIES["cpi"][0] == "CPIAUCSL"
        assert FRED_SERIES["yield_curve"][0] == "T10Y2Y"
        assert FRED_SERIES["treasury_10y"][0] == "DGS10"


class TestFredClientFetch:
    """Test FRED API fetch logic."""

    @pytest.mark.asyncio
    async def test_fetch_series_latest_success(self, fred_client, mock_fred_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_fred_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        fred_client._client = mock_client

        result = await fred_client.fetch_series_latest("CPIAUCSL", "CPI")

        assert result is not None
        assert result.value == 3.4
        assert result.series_id == "CPIAUCSL"
        assert result.observation_date == date(2026, 6, 1)

    @pytest.mark.asyncio
    async def test_fetch_skips_missing_dot_value(self, fred_client, mock_fred_missing_response):
        """FRED returns '.' for missing values — should skip and use next."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_fred_missing_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        fred_client._client = mock_client

        result = await fred_client.fetch_series_latest("CPIAUCSL", "CPI")

        assert result is not None
        assert result.value == 3.5  # Skipped "." and got second value

    @pytest.mark.asyncio
    async def test_fetch_returns_none_on_http_error(self, fred_client):
        import httpx
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=MagicMock(status_code=404)
        )
        fred_client._client = mock_client

        result = await fred_client.fetch_series_latest("INVALID", "Invalid")
        assert result is None


class TestMacroCycleAssessment:
    """Test L9 macro cycle logic."""

    @pytest.mark.asyncio
    async def test_expansion_cycle(self, fred_client):
        snapshot = MacroSnapshot(
            yield_curve=1.2,
            cpi=2.5,
            unemployment_rate=3.8,
            hy_credit_spread=3.5,
        )
        cycle = await fred_client.assess_macro_cycle(snapshot)
        assert cycle == "EXPANSION"

    @pytest.mark.asyncio
    async def test_contraction_cycle(self, fred_client):
        snapshot = MacroSnapshot(
            yield_curve=-0.8,
            cpi=5.2,
            unemployment_rate=5.5,
            hy_credit_spread=6.5,
        )
        cycle = await fred_client.assess_macro_cycle(snapshot)
        assert cycle == "CONTRACTION"

    @pytest.mark.asyncio
    async def test_peak_cycle(self, fred_client):
        snapshot = MacroSnapshot(
            yield_curve=0.1,
            cpi=5.0,
            unemployment_rate=4.0,
            hy_credit_spread=4.0,
        )
        cycle = await fred_client.assess_macro_cycle(snapshot)
        assert cycle == "PEAK"

    @pytest.mark.asyncio
    async def test_unknown_when_no_data(self, fred_client):
        snapshot = MacroSnapshot()
        cycle = await fred_client.assess_macro_cycle(snapshot)
        assert cycle == "UNKNOWN"

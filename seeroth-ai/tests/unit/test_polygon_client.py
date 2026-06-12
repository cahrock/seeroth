"""
Unit tests untuk L10 Polygon.io Client
Tests menggunakan mock — tidak perlu real API key
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.market import StockQuote, OHLCVBar
from app.services.market.polygon_client import PolygonClient


@pytest.fixture
def polygon_client():
    return PolygonClient()


@pytest.fixture
def mock_prev_day_response():
    return {
        "results": [{
            "T": "NVDA",
            "o": 120.50,
            "h": 125.80,
            "l": 119.20,
            "c": 124.30,
            "v": 45000000,
            "vw": 122.45,
            "t": 1717977600000,  # Unix ms timestamp
        }]
    }


@pytest.fixture
def mock_historical_response():
    return {
        "results": [
            {"o": 100.0, "h": 105.0, "l": 99.0, "c": 103.0, "v": 1000000, "t": 1717977600000},
            {"o": 103.0, "h": 108.0, "l": 102.0, "c": 106.0, "v": 1200000, "t": 1718064000000},
        ]
    }


class TestPolygonClientQuote:

    @pytest.mark.asyncio
    async def test_get_stock_quote_success(self, polygon_client, mock_prev_day_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_prev_day_response
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await polygon_client.get_stock_quote("NVDA")

        assert result is not None
        assert result.ticker == "NVDA"
        assert result.price == 124.30
        assert result.high == 125.80
        assert result.low == 119.20
        assert result.source == "POLYGON"

    @pytest.mark.asyncio
    async def test_get_stock_quote_empty_results(self, polygon_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await polygon_client.get_stock_quote("INVALID")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_stock_quote_uppercase(self, polygon_client, mock_prev_day_response):
        """Ticker harus selalu uppercase."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_prev_day_response
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await polygon_client.get_stock_quote("nvda")  # lowercase input

        assert result is not None
        assert result.ticker == "NVDA"  # should be uppercase


class TestPolygonClientHistory:

    @pytest.mark.asyncio
    async def test_get_historical_bars_success(self, polygon_client, mock_historical_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_historical_response
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            bars = await polygon_client.get_historical_bars(
                "NVDA",
                date(2026, 5, 1),
                date(2026, 6, 1),
                "day"
            )

        assert len(bars) == 2
        assert bars[0].ticker == "NVDA"
        assert bars[0].close == 103.0
        assert bars[1].close == 106.0

    @pytest.mark.asyncio
    async def test_get_historical_bars_empty(self, polygon_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            bars = await polygon_client.get_historical_bars(
                "INVALID",
                date(2026, 5, 1),
                date(2026, 6, 1),
            )

        assert bars == []

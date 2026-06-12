"""
L10 Data Feed — Polygon.io Client
Fetches real-time and historical market data

Endpoints used:
  /v2/aggs/ticker/{ticker}/prev          — Previous day OHLCV
  /v2/aggs/ticker/{ticker}/range/...     — Historical OHLCV bars
  /v3/reference/tickers/{ticker}         — Ticker details
  /v1/marketstatus/now                   — Market open/closed status
  /v2/snapshot/locale/us/markets/stocks/tickers/{ticker} — Real-time snapshot
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional, List

import httpx

from app.core.config import settings
from app.models.market import StockQuote, OHLCVBar, MarketStatus, TickerDetails

logger = logging.getLogger(__name__)

POLYGON_BASE_URL = "https://api.polygon.io"


class PolygonClient:
    """
    Async Polygon.io REST API client.
    Menggunakan fresh AsyncClient per request.
    """

    def __init__(self):
        self.api_key = settings.polygon_api_key
        self.base_url = POLYGON_BASE_URL

    def _auth_params(self) -> dict:
        return {"apiKey": self.api_key}

    async def get_market_status(self) -> MarketStatus:
        """Check apakah market sedang open atau closed."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    f"{self.base_url}/v1/marketstatus/now",
                    params=self._auth_params()
                )
                r.raise_for_status()
                data = r.json()

            return MarketStatus(
                market="NYSE/NASDAQ",
                status=data.get("market", "unknown"),
                server_time=data.get("serverTime"),
                exchanges=data.get("exchanges"),
            )
        except Exception as e:
            logger.error(f"Polygon market status error: {e}")
            return MarketStatus(market="NYSE/NASDAQ", status="unknown")

    async def get_stock_quote(self, ticker: str) -> Optional[StockQuote]:
        """
        Get latest stock price via previous day close + snapshot.
        Menggunakan /v2/aggs/ticker/{ticker}/prev untuk latest OHLCV.
        """
        ticker = ticker.upper()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    f"{self.base_url}/v2/aggs/ticker/{ticker}/prev",
                    params=self._auth_params()
                )
                r.raise_for_status()
                data = r.json()

            results = data.get("results", [])
            if not results:
                logger.warning(f"No price data for {ticker}")
                return None

            result = results[0]
            close = result.get("c")
            prev_close = result.get("o")  # open as reference
            price_change = (close - prev_close) if close and prev_close else None
            change_pct = (price_change / prev_close * 100) if price_change and prev_close else None

            return StockQuote(
                ticker=ticker,
                price=close,
                open=result.get("o"),
                high=result.get("h"),
                low=result.get("l"),
                close=close,
                volume=result.get("v"),
                price_change=round(price_change, 4) if price_change else None,
                change_pct=round(change_pct, 4) if change_pct else None,
                as_of=datetime.fromtimestamp(result["t"] / 1000) if result.get("t") else None,
                source="POLYGON",
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Polygon HTTP error {ticker}: {e.response.status_code} — {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Polygon quote error {ticker}: {e}")
            return None

    async def get_historical_bars(
        self,
        ticker: str,
        from_date: date,
        to_date: date,
        timespan: str = "day",
    ) -> List[OHLCVBar]:
        """
        Get historical OHLCV bars.
        timespan: minute | hour | day | week | month
        """
        ticker = ticker.upper()
        params = {
            **self._auth_params(),
            "adjusted": "true",
            "sort": "asc",
            "limit": 500,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(
                    f"{self.base_url}/v2/aggs/ticker/{ticker}/range/1/{timespan}"
                    f"/{from_date.isoformat()}/{to_date.isoformat()}",
                    params=params,
                )
                r.raise_for_status()
                data = r.json()

            results = data.get("results", [])
            bars = []
            for result in results:
                bars.append(OHLCVBar(
                    ticker=ticker,
                    time=datetime.fromtimestamp(result["t"] / 1000),
                    open=result["o"],
                    high=result["h"],
                    low=result["l"],
                    close=result["c"],
                    volume=int(result["v"]),
                    vwap=result.get("vw"),
                    source="POLYGON",
                ))

            logger.info(f"Fetched {len(bars)} {timespan} bars for {ticker}")
            return bars

        except httpx.HTTPStatusError as e:
            logger.error(f"Polygon historical error {ticker}: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Polygon historical error {ticker}: {e}")
            return []

    async def get_ticker_details(self, ticker: str) -> Optional[TickerDetails]:
        """Get company info — name, market cap, exchange, description."""
        ticker = ticker.upper()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    f"{self.base_url}/v3/reference/tickers/{ticker}",
                    params=self._auth_params()
                )
                r.raise_for_status()
                data = r.json()

            result = data.get("results", {})
            return TickerDetails(
                ticker=ticker,
                name=result.get("name"),
                market=result.get("market"),
                locale=result.get("locale"),
                primary_exchange=result.get("primary_exchange"),
                type=result.get("type"),
                currency_name=result.get("currency_name"),
                market_cap=result.get("market_cap"),
                share_class_shares_outstanding=result.get("share_class_shares_outstanding"),
                description=result.get("description"),
                homepage_url=result.get("homepage_url"),
                list_date=result.get("list_date"),
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Polygon ticker details error {ticker}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Polygon ticker details error {ticker}: {e}")
            return None

    async def get_multiple_quotes(self, tickers: List[str]) -> dict:
        """
        Fetch quotes untuk multiple tickers sekaligus.
        Returns dict: {ticker: StockQuote}
        Digunakan untuk portfolio valuation.
        """
        results = {}
        for ticker in tickers:
            quote = await self.get_stock_quote(ticker)
            if quote:
                results[ticker] = quote
            else:
                logger.warning(f"No quote returned for {ticker}")
        return results


# Singleton instance
polygon_client = PolygonClient()

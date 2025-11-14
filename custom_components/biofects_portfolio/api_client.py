"""API Client for Finnhub, CoinGecko, and Yahoo Finance."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Any

import feedparser
import finnhub
from pycoingecko import CoinGeckoAPI

from .const import (
    CACHE_CRYPTO_DATA,
    CACHE_NEWS_DATA,
    CACHE_STOCK_DATA,
    CACHE_TIMESTAMP,
    HOLDING_TYPE_CRYPTO,
    HOLDING_TYPE_STOCK,
    YAHOO_FINANCE_RSS,
    DEFAULT_NEWS_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class PortfolioAPIClient:
    """API client for portfolio data."""

    def __init__(
        self,
        finnhub_api_key: str | None = None,
        coingecko_api_key: str | None = None,
        holdings: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize the API client."""
        self.finnhub_client = None
        self.coingecko_client = CoinGeckoAPI()
        self.holdings = holdings or []
        
        if finnhub_api_key:
            self.finnhub_client = finnhub.Client(api_key=finnhub_api_key)
        
        # Cache
        self._cache: dict[str, Any] = {
            CACHE_STOCK_DATA: {},
            CACHE_CRYPTO_DATA: {},
            CACHE_NEWS_DATA: [],
            CACHE_TIMESTAMP: {
                CACHE_STOCK_DATA: None,
                CACHE_CRYPTO_DATA: None,
                CACHE_NEWS_DATA: None,
            }
        }

    def update_all(self) -> dict[str, Any]:
        """Update all holdings data."""
        result = {
            "holdings": [],
            "portfolio": {},
            "news": [],
        }

        # Separate holdings by type
        stock_holdings = [h for h in self.holdings if h.get("holding_type") == HOLDING_TYPE_STOCK]
        crypto_holdings = [h for h in self.holdings if h.get("holding_type") == HOLDING_TYPE_CRYPTO]

        # Fetch stock data (batch)
        stock_data = {}
        if stock_holdings and self.finnhub_client:
            stock_data = self._fetch_stocks_batch(stock_holdings)

        # Fetch crypto data (batch)
        crypto_data = {}
        if crypto_holdings:
            crypto_data = self._fetch_crypto_batch(crypto_holdings)

        # Calculate individual holdings
        total_value = 0.0
        total_cost = 0.0

        for holding in self.holdings:
            holding_type = holding.get("holding_type")
            symbol = holding.get("symbol", "").upper()  # Normalize to uppercase
            if holding_type == HOLDING_TYPE_CRYPTO:
                # Flexible field support: quantity, buy_price, total_invested
                quantity = float(holding.get("quantity", 0))
                buy_price = float(holding.get("buy_price", 0))
                total_invested = float(holding.get("total_invested", 0))
                # Calculate missing value if only two are present
                fields_filled = sum([quantity > 0, buy_price > 0, total_invested > 0])
                if fields_filled >= 2:
                    if quantity > 0 and buy_price > 0 and total_invested == 0:
                        total_invested = quantity * buy_price
                    elif total_invested > 0 and buy_price > 0 and quantity == 0:
                        quantity = total_invested / buy_price if buy_price else 0
                    elif total_invested > 0 and quantity > 0 and buy_price == 0:
                        buy_price = total_invested / quantity if quantity else 0
                # If only one or zero fields, all will be zero
                current_price = crypto_data.get(symbol, 0.0)
                if current_price == 0:
                    _LOGGER.warning(f"Price for {symbol} (crypto) is 0 - check API response")
                current_value = quantity * current_price
                profit_loss = current_value - total_invested
                percent_change = (profit_loss / total_invested * 100) if total_invested > 0 else 0
                result["holdings"].append({
                    "symbol": symbol,
                    "holding_type": holding_type,
                    "quantity": quantity,
                    "buy_price": buy_price,
                    "current_price": current_price,
                    "total_value": current_value,
                    "total_cost": total_invested,
                    "total_invested": total_invested,
                    "gain_loss": profit_loss,
                    "gain_loss_percent": percent_change,
                    "last_updated": datetime.now().isoformat(),
                })
                total_value += current_value
                total_cost += total_invested
            else:
                quantity = float(holding.get("quantity", 0))
                buy_price = float(holding.get("buy_price", 0))
                current_price = stock_data.get(symbol, 0.0)
                if current_price == 0:
                    _LOGGER.warning(f"Price for {symbol} (stock) is 0 - check API response")
                total_holding_value = current_price * quantity
                total_holding_cost = holding.get("total_invested", buy_price * quantity)
                gain_loss = total_holding_value - total_holding_cost
                gain_loss_pct = (gain_loss / total_holding_cost * 100) if total_holding_cost > 0 else 0
                result["holdings"].append({
                    "symbol": symbol,
                    "holding_type": holding_type,
                    "quantity": quantity,
                    "buy_price": buy_price,
                    "current_price": current_price,
                    "total_value": total_holding_value,
                    "total_cost": total_holding_cost,
                    "total_invested": holding.get("total_invested"),
                    "gain_loss": gain_loss,
                    "gain_loss_percent": gain_loss_pct,
                    "last_updated": datetime.now().isoformat(),
                })
                total_value += total_holding_value
                total_cost += total_holding_cost

        # Calculate portfolio totals
        portfolio_gain_loss = total_value - total_cost
        portfolio_gain_loss_pct = (portfolio_gain_loss / total_cost * 100) if total_cost > 0 else 0

        result["portfolio"] = {
            "total_holdings": len(self.holdings),
            "stock_count": len(stock_holdings),
            "crypto_count": len(crypto_holdings),
            "total_value": total_value,
            "total_cost": total_cost,
            "total_gain_loss": portfolio_gain_loss,
            "total_gain_loss_percent": portfolio_gain_loss_pct,
            "last_updated": datetime.now().isoformat(),
        }

        # Fetch news
        result["news"] = self._fetch_news()

        return result

    def _fetch_stocks_batch(self, stock_holdings: list[dict]) -> dict[str, float]:
        """Fetch stock prices in batch using Finnhub."""
        stock_prices = {}
        
        if not self.finnhub_client:
            _LOGGER.warning("Finnhub client not initialized")
            return stock_prices

        # Check cache
        cache_time = self._cache[CACHE_TIMESTAMP].get(CACHE_STOCK_DATA)
        if cache_time and (time.time() - cache_time) < 300:  # 5 minutes cache
            _LOGGER.debug("Using cached stock data")
            return self._cache[CACHE_STOCK_DATA]

        try:
            for holding in stock_holdings:
                symbol = holding.get("symbol", "").upper()  # Ensure uppercase
                if not symbol:
                    continue
                
                try:
                    # Fetch quote from Finnhub
                    _LOGGER.info(f"Fetching quote for {symbol} from Finnhub")
                    quote = self.finnhub_client.quote(symbol)
                    _LOGGER.debug(f"Finnhub response for {symbol}: {quote}")
                    
                    if quote and "c" in quote and quote["c"] > 0:  # 'c' is current price
                        stock_prices[symbol] = float(quote["c"])
                        _LOGGER.info(f"✓ Fetched price for {symbol}: ${stock_prices[symbol]}")
                    else:
                        _LOGGER.warning(f"No valid price data for stock {symbol}. Response: {quote}")
                        stock_prices[symbol] = 0.0
                except Exception as err:
                    _LOGGER.error(f"Error fetching stock {symbol}: {err}", exc_info=True)
                    stock_prices[symbol] = 0.0

            # Update cache
            self._cache[CACHE_STOCK_DATA] = stock_prices
            self._cache[CACHE_TIMESTAMP][CACHE_STOCK_DATA] = time.time()
            
        except Exception as err:
            _LOGGER.error(f"Error in batch stock fetch: {err}")

        return stock_prices

    def _fetch_crypto_batch(self, crypto_holdings: list[dict]) -> dict[str, float]:
        """Fetch crypto prices in batch using CoinGecko."""
        crypto_prices = {}

        # Check cache
        cache_time = self._cache[CACHE_TIMESTAMP].get(CACHE_CRYPTO_DATA)
        if cache_time and (time.time() - cache_time) < 300:  # 5 minutes cache
            _LOGGER.debug("Using cached crypto data")
            return self._cache[CACHE_CRYPTO_DATA]

        try:
            # Build list of crypto IDs
            # Map common symbols to CoinGecko IDs
            symbol_to_id = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "USDT": "tether",
                "BNB": "binancecoin",
                "SOL": "solana",
                "ADA": "cardano",
                "DOGE": "dogecoin",
                "XRP": "ripple",
                "DOT": "polkadot",
                "MATIC": "matic-network",
            }

            crypto_ids = []
            symbol_map = {}
            
            for holding in crypto_holdings:
                symbol = holding.get("symbol", "").upper()
                # Remove common suffixes
                clean_symbol = symbol.replace("USDT", "").replace("USD", "").replace("BUSD", "")
                
                # Get CoinGecko ID
                gecko_id = symbol_to_id.get(clean_symbol, symbol.lower())
                crypto_ids.append(gecko_id)
                symbol_map[gecko_id] = symbol

            if crypto_ids:
                # Batch fetch from CoinGecko
                response = self.coingecko_client.get_price(
                    ids=",".join(crypto_ids),
                    vs_currencies="usd"
                )

                for gecko_id, data in response.items():
                    original_symbol = symbol_map.get(gecko_id)
                    if original_symbol and "usd" in data:
                        crypto_prices[original_symbol] = float(data["usd"])
                        _LOGGER.debug(f"Fetched price for {original_symbol}: {crypto_prices[original_symbol]}")

            # Update cache
            self._cache[CACHE_CRYPTO_DATA] = crypto_prices
            self._cache[CACHE_TIMESTAMP][CACHE_CRYPTO_DATA] = time.time()

        except Exception as err:
            _LOGGER.error(f"Error in batch crypto fetch: {err}")

        return crypto_prices

    def _fetch_news(self) -> list[dict[str, str]]:
        """Fetch finance news from Yahoo Finance RSS."""
        # Check cache (update hourly)
        cache_time = self._cache[CACHE_TIMESTAMP].get(CACHE_NEWS_DATA)
        if cache_time and (time.time() - cache_time) < (DEFAULT_NEWS_UPDATE_INTERVAL * 60):
            _LOGGER.debug("Using cached news data")
            return self._cache[CACHE_NEWS_DATA]

        news_items = []
        try:
            feed = feedparser.parse(YAHOO_FINANCE_RSS)
            
            for entry in feed.entries[:10]:  # Get top 10 news items
                news_items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                })

            # Update cache
            self._cache[CACHE_NEWS_DATA] = news_items
            self._cache[CACHE_TIMESTAMP][CACHE_NEWS_DATA] = time.time()
            
            _LOGGER.debug(f"Fetched {len(news_items)} news items")

        except Exception as err:
            _LOGGER.error(f"Error fetching news: {err}")

        return news_items

    def test_connection(self) -> bool:
        """Test API connections."""
        try:
            # Test Finnhub
            if self.finnhub_client:
                self.finnhub_client.quote("AAPL")
            
            # Test CoinGecko
            self.coingecko_client.ping()
            
            return True
        except Exception as err:
            _LOGGER.error(f"Connection test failed: {err}")
            return False

"""Constants for the Biofects Portfolio Tracker integration."""

DOMAIN = "biofects_portfolio"

# Configuration
CONF_FINNHUB_API_KEY = "finnhub_api_key"
CONF_COINGECKO_API_KEY = "coingecko_api_key"
CONF_HOLDINGS = "holdings"
CONF_UPDATE_INTERVAL = "update_interval"

# Defaults
DEFAULT_UPDATE_INTERVAL = 10  # minutes
DEFAULT_NEWS_UPDATE_INTERVAL = 60  # minutes

# Holding types
HOLDING_TYPE_STOCK = "stock"
HOLDING_TYPE_CRYPTO = "crypto"

# Holding fields
CONF_SYMBOL = "symbol"
CONF_QUANTITY = "quantity"
CONF_BUY_PRICE = "buy_price"
CONF_HOLDING_TYPE = "holding_type"
CONF_PURCHASE_DATE = "purchase_date"  # New: track when purchased
CONF_LOT_ID = "lot_id"  # New: unique ID for each purchase

# Cache keys
CACHE_STOCK_DATA = "stock_data"
CACHE_CRYPTO_DATA = "crypto_data"
CACHE_NEWS_DATA = "news_data"
CACHE_TIMESTAMP = "timestamp"

# Sensor attributes
ATTR_SYMBOL = "symbol"
ATTR_QUANTITY = "quantity"
ATTR_BUY_PRICE = "buy_price"
ATTR_CURRENT_PRICE = "current_price"
ATTR_TOTAL_VALUE = "total_value"
ATTR_TOTAL_COST = "total_cost"
ATTR_GAIN_LOSS = "gain_loss"
ATTR_GAIN_LOSS_PCT = "gain_loss_percent"
ATTR_LAST_UPDATED = "last_updated"
ATTR_HOLDING_TYPE = "holding_type"

# Portfolio attributes
ATTR_TOTAL_HOLDINGS = "total_holdings"
ATTR_STOCK_COUNT = "stock_count"
ATTR_CRYPTO_COUNT = "crypto_count"
ATTR_TOTAL_PORTFOLIO_VALUE = "total_value"
ATTR_TOTAL_PORTFOLIO_COST = "total_cost"
ATTR_PORTFOLIO_GAIN_LOSS = "total_gain_loss"
ATTR_PORTFOLIO_GAIN_LOSS_PCT = "total_gain_loss_percent"

# API URLs
YAHOO_FINANCE_RSS = "https://finance.yahoo.com/news/rssindex"

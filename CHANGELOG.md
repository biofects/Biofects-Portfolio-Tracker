# Changelog

## [1.0.0] - 2025-11-02

### Initial Release

#### Core Features
- **Stock tracking via Finnhub API** with real-time prices
- **Cryptocurrency tracking via CoinGecko** (completely free, no API key needed)
- **Portfolio performance calculations** - gain/loss tracking for individual holdings and total portfolio
- **Financial news feed** from Yahoo Finance RSS
- **Batch API calls** for efficiency (1 call for all stocks, 1 for all crypto)
- **Smart caching system** (5-minute cache for prices, 60-minute for news)

#### User Interface
- **Config Flow setup** - Easy UI-based configuration
- **Options menu** with dropdown selector for post-installation management:
  - Update refresh interval
  - Update Finnhub API key
  - Add new holdings
  - Remove holdings
  - View all holdings
- **Symbol normalization** - Automatically converts symbols to uppercase (NVDA, BTC, etc.)

#### Sensors Created
- `sensor.portfolio_summary` - Total portfolio value with attributes (gain/loss, performance %)
- `sensor.holding_[symbol]` - Individual holding value with full details
- `sensor.[symbol]_price` - Current price sensors optimized for graphing
- `sensor.portfolio_news` - Latest financial news (10 items)

#### Technical Features
- Proper Home Assistant device classes (MONETARY) for all sensors
- State class support (TOTAL for values, MEASUREMENT for prices)
- Configurable update intervals (1-60 minutes, default 10)
- Full error logging and debugging support
- Service integrations for programmatic holding management

### Requirements
- Finnhub API key (free tier: 60 calls/minute)
- CoinGecko: No API key needed (uses free public API)

### Compatibility
- Home Assistant 2023.1+
- Docker installations supported
- HACS compatible

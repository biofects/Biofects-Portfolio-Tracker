
# 💼 Biofects Portfolio Tracker for Home Assistant

A comprehensive Home Assistant custom integration that tracks stocks, cryptocurrencies, and portfolio performance in near real-time using Finnhub and CoinGecko APIs. View everything from your Lovelace dashboard with charts, statistics, and a financial news ticker.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue)

---
## 💸 Donations Appreciated!
If you find this plugin useful, please consider donating. Your support is greatly appreciated!

### Sponsor me on GitHub
[![Sponsor Me](https://img.shields.io/badge/Sponsor%20Me-%F0%9F%92%AA-purple?style=for-the-badge)](https://github.com/sponsors/biofects?frequency=recurring&sponsor=biofects) 

### or
## Paypal

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TWRQVYJWC77E6)
---

## 🌟 Features

### 📊 Unified Portfolio Tracking
- **Multi-Asset Support**: Track both stocks and cryptocurrencies via Finnhub API in one unified portfolio
- **Real-Time Updates**: Automatic price updates on a configurable schedule (default: every 10 minutes)
- **Efficient API Usage**: Batch API calls minimize rate limits and maximize performance
- **Dynamic Entity Management**: Entities are automatically created and removed based on your holdings configuration

### 💰 Comprehensive Analytics
**For each holding:**
- Current market price
- Total position value
- Cost basis
- Gain/Loss (absolute $ and %)
- Performance tracking

**For your entire portfolio:**
- Total portfolio value
- Total cost basis
- Overall gain/loss
- Portfolio performance percentage
- Holdings breakdown (stocks vs. crypto)

### 📰 Financial News Integration
- Live financial news feed from Yahoo Finance RSS
- Cached hourly to minimize API load
- Accessible as sensor attributes for custom dashboards


### 🎯 Smart Features
- **Intelligent caching** reduces API calls (5-min for prices, 60-min for news)
- **Symbol normalization** - automatically converts to uppercase (NVDA, BTC, etc.)
- **Post-install configuration** - add/remove holdings and update API keys anytime

### 🎨 Easy Configuration
- User-friendly Config Flow UI
- No YAML editing required (but supported!)
- Add unlimited holdings
- Modify settings through Home Assistant UI

## 📦 Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/biofects/Biofects-Portfolio-Tracker`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install"
9. Restart Home Assistant

### Manual Installation

2. Copy the `custom_components/biofects_portfolio` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## 🔧 Configuration

### API Keys Setup

**Required:**

**Finnhub** (for stocks): 
- Free tier: 60 API calls/minute
- Get your API key from the dashboard
   
**Optional:**
- No separate API key needed for crypto

### Setup via UI
5. Add your holdings:
   - **Symbol**: Stock ticker (e.g., `AAPL`) or crypto symbol (e.g., `BTC`)
### Post-Installation Configuration

2. Find **Biofects Portfolio Tracker**
3. Click **Configure** (⚙️ gear icon)
   - Remove holdings
   - View all holdings

### Portfolio Summary Sensor
`sensor.portfolio_summary`
- **State**: Total portfolio value in USD
- **Attributes**:
  - `total_holdings`: Number of holdings
  - `stock_count`: Number of stock positions
  - `crypto_count`: Number of crypto positions
  - `total_cost`: Total cost basis
  - `total_gain_loss`: Total gain/loss in USD
  - `total_gain_loss_percent`: Portfolio performance %
  - `last_updated`: Last update timestamp

### Individual Holding Sensors
For each holding, two sensors are created:

**`sensor.holding_[symbol]`** - Holding details
- **State**: Total position value in USD
- **Attributes**:
  - `symbol`: Asset symbol
  - `holding_type`: `stock` or `crypto`
  - `quantity`: Number of shares/coins
  - `buy_price`: Purchase price
  - `current_price`: Current market price
  - `total_value`: Position value
  - `gain_loss`: Gain/loss amount
  - `gain_loss_percent`: Gain/loss percentage



## 🧩 Requirements for Dashboard (Auto Layout)

If you want to use the advanced auto-discovery dashboard (`sample-layout-auto.yml`), you must install these HACS frontend cards:

- [auto-entities](https://github.com/thomasloven/lovelace-auto-entities) – Dynamic entity lists
- [stack-in-card](https://github.com/custom-cards/stack-in-card) – Card organization
- [layout-card](https://github.com/thomasloven/lovelace-layout-card) – Advanced layouts

Install these from HACS → Frontend before using the auto layout sample.

---
## 🎨 Dashboard Setup

### Dashboard Versions Available
#### 1. Basic Layout ([examples/sample-layout.yml](examples/sample-layout.yml))
- **Works immediately** with no additional cards required
- Uses standard Home Assistant cards only
- **Manual**: You need to add entity names when you add new holdings
- Perfect for getting started quickly

#### 2. Auto Layout ([examples/sample-layout-auto.yml](examples/sample-layout-auto.yml))
- **Requires HACS cards** but provides automatic discovery
- **Dynamic**: Automatically shows new holdings as you add them
- No manual entity configuration needed

### Required HACS Frontend Cards (for Auto Layout)

For the auto sample dashboard layout to work, install these cards via HACS:

1. **auto-entities** - For dynamic entity lists
   - HACS → Frontend → Search "auto-entities"
2. **stack-in-card** - For card organization
   - HACS → Frontend → Search "stack-in-card"  
3. **layout-card** - For advanced layouts
   - HACS → Frontend → Search "layout-card"

### Quick Start

1. **Basic Setup**: [View or copy the sample-layout.yml](examples/sample-layout.yml) – works immediately!
2. **Enhanced Setup**: Install HACS cards, then [view or copy sample-layout-auto.yml](examples/sample-layout-auto.yml) for automatic entity discovery

### News Feed Sensor
  - `current_price`: Current market price
  - `total_cost`: Position cost basis
  - `gain_loss`: Position gain/loss in USD
  - `gain_loss_percent`: Position performance %
  - `last_updated`: Last update timestamp

- **State**: Number of news items
- **Attributes**:
  - `news_items`: Array of news objects with:
    - `title`: News headline
    - `link`: Article URL
    - `published`: Publication date
    - `summary`: Article summary

## 🎨 Lovelace Dashboard Examples

### Simple Portfolio Card

title: 💼 My Portfolio
entities:
  - entity: sensor.portfolio_summary
    name: Total Value
    icon: mdi:wallet
  - type: attribute
    entity: sensor.portfolio_summary
    attribute: total_gain_loss
    name: Gain/Loss
    suffix: USD
    attribute: total_gain_loss_percent
    name: Performance
    suffix: '%'
```

### Holdings List Card

  - entity: sensor.holding_aapl
    name: Apple (AAPL)
    secondary_info: attribute
    attribute: gain_loss_percent
  - entity: sensor.holding_tsla
    name: Tesla (TSLA)
    secondary_info: attribute
    attribute: gain_loss_percent
  - entity: sensor.holding_btc
    name: Bitcoin
    secondary_info: attribute
    attribute: gain_loss_percent
```

### Portfolio Chart (Using ApexCharts)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Portfolio Performance
graph_span: 7d
    name: Portfolio Value
```

### Advanced Portfolio Dashboard with Statistics

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-template-card
    primary: Portfolio Value
    secondary: ${{ states('sensor.portfolio_summary') }}
    icon: mdi:wallet
    icon_color: >
      {% if state_attr('sensor.portfolio_summary', 'total_gain_loss') | float > 0 %}
        green
      {% else %}
        red
      {% endif %}
    
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-template-card
        primary: Stocks
        secondary: '{{ state_attr("sensor.portfolio_summary", "stock_count") }}'
        icon: mdi:chart-line
        
      - type: custom:mushroom-template-card
        primary: Crypto
        secondary: '{{ state_attr("sensor.portfolio_summary", "crypto_count") }}'
        icon: mdi:currency-btc
        
  - type: custom:mushroom-template-card
    primary: >
      {% set gl = state_attr('sensor.portfolio_summary', 'total_gain_loss') | float %}
      {% if gl > 0 %}📈{% else %}📉{% endif %}
      {{ '%.2f' | format(gl) }} USD
    secondary: >
      {{ '%.2f' | format(state_attr('sensor.portfolio_summary', 'total_gain_loss_percent') | float) }}%
    icon: mdi:trending-up
    icon_color: >
      {% if state_attr('sensor.portfolio_summary', 'total_gain_loss') | float > 0 %}
        green
      {% else %}
        red
      {% endif %}
```

### News Ticker Card

```yaml
type: markdown
content: >
  ## 📰 Market News
  
  {% for item in state_attr('sensor.portfolio_news', 'news_items')[:5] %}
  **[{{ item.title }}]({{ item.link }})**
  
  {{ item.published }}
  
  ---
  {% endfor %}
```

### Complete Dashboard Example

```yaml
views:
  - title: Portfolio
    path: portfolio
    icon: mdi:wallet
    cards:
      - type: vertical-stack
        cards:
          # Summary Section
          - type: custom:mushroom-title-card
            title: My Investment Portfolio
            
          - type: horizontal-stack
            cards:
              - type: statistic
                entity: sensor.portfolio_summary
                name: Total Value
                
              - type: custom:mushroom-template-card
                primary: >
                  {{ '%.2f' | format(state_attr('sensor.portfolio_summary', 'total_gain_loss_percent') | float) }}%
                secondary: Performance
                icon: mdi:chart-line
                icon_color: >
                  {% if state_attr('sensor.portfolio_summary', 'total_gain_loss') | float > 0 %}
                    green
                  {% else %}
                    red
                  {% endif %}
          
          # Chart Section
          - type: custom:apexcharts-card
            header:
              show: true
              title: 7-Day Performance
            graph_span: 7d
            series:
              - entity: sensor.portfolio_summary
                name: Portfolio Value
                stroke_width: 3
                
          # Holdings Section
          - type: custom:auto-entities
            card:
              type: entities
              title: 📊 Holdings
            filter:
              include:
                - entity_id: sensor.holding_*
                  options:
                    type: custom:multiple-entity-row
                    secondary_info:
                      attribute: gain_loss_percent
                      name: false
                      suffix: '%'
                    entities:
                      - attribute: current_price
                        name: Price
                      - attribute: quantity
                        name: Qty
                        
          # News Section
          - type: markdown
            title: 📰 Latest Market News
            content: >
              {% for item in state_attr('sensor.portfolio_news', 'news_items')[:5] %}
              **[{{ item.title }}]({{ item.link }})**
              
              *{{ item.published }}*
              
              ---
              {% endfor %}
```

## 🔄 Automation Examples

### Daily Portfolio Report

```yaml
automation:
  - alias: Daily Portfolio Report
    trigger:
      platform: time
      at: "09:00:00"
    action:
      service: notify.mobile_app
      data:
        title: "📊 Daily Portfolio Update"
        message: >
          Portfolio Value: ${{ states('sensor.portfolio_summary') }}
          Today's Change: ${{ state_attr('sensor.portfolio_summary', 'total_gain_loss') }}
          Performance: {{ state_attr('sensor.portfolio_summary', 'total_gain_loss_percent') }}%
```

### Alert on Big Gains/Losses

```yaml
automation:
  - alias: Portfolio Alert - Big Gain
    trigger:
      platform: numeric_state
      entity_id: sensor.portfolio_summary
      attribute: total_gain_loss_percent
      above: 5
    action:
      service: notify.mobile_app
      data:
        title: "🚀 Portfolio up {{ trigger.to_state.attributes.total_gain_loss_percent }}%!"
        message: "Your portfolio is performing great!"

  - alias: Portfolio Alert - Big Loss
    trigger:
      platform: numeric_state
      entity_id: sensor.portfolio_summary
      attribute: total_gain_loss_percent
      below: -5
    action:
      service: notify.mobile_app
      data:
        title: "⚠️ Portfolio down {{ trigger.to_state.attributes.total_gain_loss_percent }}%"
        message: "Consider reviewing your positions."
```

## 🛠️ Troubleshooting

### API Connection Issues
- Verify your API keys are correct
- Check API rate limits (Finnhub free tier: 60 calls/min)
- Ensure Home Assistant can reach external APIs

### Holdings Not Updating
- Check the update interval setting (default: 10 minutes)
- Verify symbols are correct (use proper stock tickers)
- Check Home Assistant logs for errors

### Crypto Symbols Not Working
Use these common mappings:
- Bitcoin: `BTC`
- Ethereum: `ETH`
- Binance Coin: `BNB`
- Solana: `SOL`
- Cardano: `ADA`

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.biofects_portfolio: debug
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💬 Support

- Report bugs: [GitHub Issues](https://github.com/biofects/Biofects-Portfolio-Tracker/issues)
- Feature requests: [GitHub Discussions](https://github.com/biofects/Biofects-Portfolio-Tracker/discussions)

## 📚 API Documentation

- [Finnhub API](https://finnhub.io/docs/api)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)

## ⚠️ Disclaimer

This integration is for informational purposes only. It does not provide financial advice. Always do your own research before making investment decisions.

---

**Made with ❤️ by Biofects**

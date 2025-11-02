# 🚀 Quick Start Guide

Get your portfolio tracker running in 5 minutes!

## Step 1: Get API Keys (2 minutes)

### Finnhub (Required for Stocks)
1. Go to https://finnhub.io/register
2. Sign up (free)
3. Copy your API key from the dashboard

### CoinGecko (Optional - Already Free!)
- ✅ **No API key needed!** Works completely free
- The integration uses CoinGecko's public API
- Just add crypto holdings and it works automatically
- Optional: Get API key for higher limits at https://www.coingecko.com/en/api/pricing

## Step 2: Install Integration

The integration is already installed at:
```
/home/tfam/tfam-scripts/home-assistant/home-assistant/config/custom_components/biofects_portfolio/
```

## Step 3: Restart Home Assistant

```bash
# Restart Home Assistant
sudo systemctl restart home-assistant@homeassistant
```

Or: Settings → System → Restart

## Step 4: Configure (1 minute)

1. Settings → Devices & Services
2. Click "+ Add Integration"
3. Search "Biofects Portfolio"
4. Enter your Finnhub API key (CoinGecko field can be left blank!)
5. Add holdings:
   ```
   Symbol: AAPL
   Type: stock
   Quantity: 10
   Buy Price: 150.00
   ```
6. Click "Add another" for more holdings or uncheck to finish

## Step 5: View Your Portfolio

Your sensors are ready:
- `sensor.portfolio_summary` - Total value & performance
- `sensor.holding_*` - Individual holdings
- `sensor.portfolio_news` - Market news

## Quick Dashboard

Add this to Lovelace:

```yaml
type: entities
title: 💼 My Portfolio
entities:
  - entity: sensor.portfolio_summary
    name: Total Value
  - type: attribute
    entity: sensor.portfolio_summary
    attribute: total_gain_loss_percent
    name: Performance
    suffix: '%'
```

## Example Holdings

**Stocks:**
- AAPL (Apple)
- TSLA (Tesla)
- MSFT (Microsoft)
- GOOGL (Google)
- AMZN (Amazon)

**Crypto:**
- BTC (Bitcoin)
- ETH (Ethereum)
- SOL (Solana)
- ADA (Cardano)
- MATIC (Polygon)

## Common Sensors

After setup, check Developer Tools → States:

```
sensor.portfolio_summary
sensor.holding_aapl
sensor.holding_tsla
sensor.holding_btc
sensor.portfolio_news
```

## Troubleshooting

**Integration not found?**
- Restart Home Assistant
- Check `/config/custom_components/biofects_portfolio/` exists

**API errors?**
- Verify API key is correct
- Check you have internet access
- Free tier: max 60 calls/minute

**Need help?**
- Check logs: Settings → System → Logs
- See full docs: [README.md](README.md)
- See testing guide: [TESTING.md](TESTING.md)

---

**That's it!** Your portfolio tracker is ready to use. 

For advanced dashboards, automations, and more, see the [README.md](README.md) and [examples](examples/) directory.

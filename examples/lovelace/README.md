# Example Lovelace Dashboards for Biofects Portfolio Tracker

This directory contains ready-to-use Lovelace dashboard configurations for displaying your portfolio data.

## Files

- `simple-dashboard.yaml` - Basic portfolio overview
- `advanced-dashboard.yaml` - Complete dashboard with charts and news
- `mobile-dashboard.yaml` - Mobile-optimized view
- `entities-card-examples.yaml` - Various entity card configurations

## Installation

1. Copy the desired dashboard configuration
2. Go to your Home Assistant Lovelace dashboard
3. Click the three dots menu → "Edit Dashboard"
4. Click the three dots menu again → "Raw configuration editor"
5. Paste the configuration or add sections to your existing dashboard

## Required Custom Cards

Some examples use custom cards available through HACS:

- **ApexCharts Card**: For beautiful charts
  - Install: HACS → Frontend → Search "ApexCharts Card"
  
- **Mushroom Cards**: For modern UI elements
  - Install: HACS → Frontend → Search "Mushroom"
  
- **Auto Entities**: For dynamic entity lists
  - Install: HACS → Frontend → Search "Auto Entities"
  
- **Multiple Entity Row**: For compact entity display
  - Install: HACS → Frontend → Search "Multiple Entity Row"

## Customization

Feel free to modify colors, icons, and layouts to match your preferences. All examples use standard Home Assistant templating syntax.

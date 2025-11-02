"""Platform for sensor integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_DOLLAR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTR_SYMBOL,
    ATTR_QUANTITY,
    ATTR_BUY_PRICE,
    ATTR_CURRENT_PRICE,
    ATTR_TOTAL_VALUE,
    ATTR_TOTAL_COST,
    ATTR_GAIN_LOSS,
    ATTR_GAIN_LOSS_PCT,
    ATTR_LAST_UPDATED,
    ATTR_HOLDING_TYPE,
    ATTR_TOTAL_HOLDINGS,
    ATTR_STOCK_COUNT,
    ATTR_CRYPTO_COUNT,
    ATTR_TOTAL_PORTFOLIO_VALUE,
    ATTR_TOTAL_PORTFOLIO_COST,
    ATTR_PORTFOLIO_GAIN_LOSS,
    ATTR_PORTFOLIO_GAIN_LOSS_PCT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[SensorEntity] = []

    # Add portfolio summary sensor
    entities.append(PortfolioSummarySensor(coordinator, entry))

    # Add individual holding sensors
    if coordinator.data and "holdings" in coordinator.data:
        for idx, holding in enumerate(coordinator.data["holdings"]):
            entities.append(HoldingSensor(coordinator, entry, idx))
            # Add price sensor for graphing
            entities.append(HoldingPriceSensor(coordinator, entry, idx))

    # Add news sensor
    entities.append(PortfolioNewsSensor(coordinator, entry))

    async_add_entities(entities)


class PortfolioSummarySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Portfolio Summary sensor."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_portfolio_summary"
        self._attr_name = "Portfolio Summary"
        self._attr_icon = "mdi:wallet"
        self._attr_native_unit_of_measurement = CURRENCY_DOLLAR
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_device_class = SensorDeviceClass.MONETARY

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "portfolio" in self.coordinator.data:
            return self.coordinator.data["portfolio"].get(ATTR_TOTAL_PORTFOLIO_VALUE, 0.0)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data or "portfolio" not in self.coordinator.data:
            return {}

        portfolio = self.coordinator.data["portfolio"]
        return {
            ATTR_TOTAL_HOLDINGS: portfolio.get(ATTR_TOTAL_HOLDINGS, 0),
            ATTR_STOCK_COUNT: portfolio.get(ATTR_STOCK_COUNT, 0),
            ATTR_CRYPTO_COUNT: portfolio.get(ATTR_CRYPTO_COUNT, 0),
            ATTR_TOTAL_PORTFOLIO_COST: portfolio.get(ATTR_TOTAL_PORTFOLIO_COST, 0.0),
            ATTR_PORTFOLIO_GAIN_LOSS: portfolio.get(ATTR_PORTFOLIO_GAIN_LOSS, 0.0),
            ATTR_PORTFOLIO_GAIN_LOSS_PCT: portfolio.get(ATTR_PORTFOLIO_GAIN_LOSS_PCT, 0.0),
            ATTR_LAST_UPDATED: portfolio.get(ATTR_LAST_UPDATED),
        }


class HoldingSensor(CoordinatorEntity, SensorEntity):
    """Representation of an individual holding sensor."""

    def __init__(self, coordinator, entry: ConfigEntry, index: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._index = index
        
        # Get initial holding data for setup
        holding = self._get_holding()
        symbol = holding.get(ATTR_SYMBOL, f"holding_{index}")
        
        self._attr_unique_id = f"{entry.entry_id}_holding_{symbol}_{index}"
        self._attr_name = f"Holding {symbol}"
        self._attr_native_unit_of_measurement = CURRENCY_DOLLAR
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_device_class = SensorDeviceClass.MONETARY

    def _get_holding(self) -> dict[str, Any]:
        """Get holding data from coordinator."""
        if (
            self.coordinator.data
            and "holdings" in self.coordinator.data
            and len(self.coordinator.data["holdings"]) > self._index
        ):
            return self.coordinator.data["holdings"][self._index]
        return {}

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        holding = self._get_holding()
        holding_type = holding.get(ATTR_HOLDING_TYPE, "")
        
        if holding_type == "crypto":
            return "mdi:currency-btc"
        return "mdi:chart-line"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        holding = self._get_holding()
        return holding.get(ATTR_TOTAL_VALUE)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        holding = self._get_holding()
        
        if not holding:
            return {}

        return {
            ATTR_SYMBOL: holding.get(ATTR_SYMBOL),
            ATTR_HOLDING_TYPE: holding.get(ATTR_HOLDING_TYPE),
            ATTR_QUANTITY: holding.get(ATTR_QUANTITY),
            ATTR_BUY_PRICE: holding.get(ATTR_BUY_PRICE),
            ATTR_CURRENT_PRICE: holding.get(ATTR_CURRENT_PRICE),
            ATTR_TOTAL_COST: holding.get(ATTR_TOTAL_COST),
            ATTR_GAIN_LOSS: holding.get(ATTR_GAIN_LOSS),
            ATTR_GAIN_LOSS_PCT: holding.get(ATTR_GAIN_LOSS_PCT),
            ATTR_LAST_UPDATED: holding.get(ATTR_LAST_UPDATED),
        }


class HoldingPriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a holding's current price (for graphing)."""

    def __init__(self, coordinator, entry: ConfigEntry, index: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._index = index
        
        # Get initial holding data for setup
        holding = self._get_holding()
        symbol = holding.get(ATTR_SYMBOL, f"holding_{index}")
        
        self._attr_unique_id = f"{entry.entry_id}_price_{symbol}_{index}"
        self._attr_name = f"{symbol} Price"
        self._attr_native_unit_of_measurement = CURRENCY_DOLLAR
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.MONETARY

    def _get_holding(self) -> dict[str, Any]:
        """Get holding data from coordinator."""
        if (
            self.coordinator.data
            and "holdings" in self.coordinator.data
            and len(self.coordinator.data["holdings"]) > self._index
        ):
            return self.coordinator.data["holdings"][self._index]
        return {}

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        holding = self._get_holding()
        holding_type = holding.get(ATTR_HOLDING_TYPE, "")
        
        if holding_type == "crypto":
            return "mdi:currency-btc"
        return "mdi:chart-line"

    @property
    def native_value(self) -> float | None:
        """Return the current price."""
        holding = self._get_holding()
        return holding.get(ATTR_CURRENT_PRICE, 0.0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        holding = self._get_holding()
        
        if not holding:
            return {}

        return {
            ATTR_SYMBOL: holding.get(ATTR_SYMBOL),
            ATTR_HOLDING_TYPE: holding.get(ATTR_HOLDING_TYPE),
            ATTR_LAST_UPDATED: holding.get(ATTR_LAST_UPDATED),
        }


class PortfolioNewsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Portfolio News sensor."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_portfolio_news"
        self._attr_name = "Portfolio News"
        self._attr_icon = "mdi:newspaper-variant-outline"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor (number of news items)."""
        if self.coordinator.data and "news" in self.coordinator.data:
            return len(self.coordinator.data["news"])
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data or "news" not in self.coordinator.data:
            return {"news_items": []}

        news_items = self.coordinator.data["news"]
        return {
            "news_items": news_items,
            "last_updated": datetime.now().isoformat(),
        }

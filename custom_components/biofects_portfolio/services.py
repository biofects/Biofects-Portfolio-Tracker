"""Services for Biofects Portfolio Tracker."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_SYMBOL, CONF_QUANTITY, CONF_BUY_PRICE, CONF_HOLDING_TYPE

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_HOLDING = "add_holding"
SERVICE_REMOVE_HOLDING = "remove_holding"
SERVICE_UPDATE_HOLDING = "update_holding"

ADD_HOLDING_SCHEMA = vol.Schema({
    vol.Required(CONF_SYMBOL): cv.string,
    vol.Required(CONF_HOLDING_TYPE): vol.In(["stock", "crypto"]),
    vol.Required(CONF_QUANTITY): vol.Coerce(float),
    vol.Required(CONF_BUY_PRICE): vol.Coerce(float),
})

REMOVE_HOLDING_SCHEMA = vol.Schema({
    vol.Required(CONF_SYMBOL): cv.string,
})

UPDATE_HOLDING_SCHEMA = vol.Schema({
    vol.Required(CONF_SYMBOL): cv.string,
    vol.Optional(CONF_QUANTITY): vol.Coerce(float),
    vol.Optional(CONF_BUY_PRICE): vol.Coerce(float),
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Biofects Portfolio."""

    async def async_handle_add_holding(call: ServiceCall) -> None:
        """Handle add holding service call."""
        symbol = call.data[CONF_SYMBOL]
        holding_type = call.data[CONF_HOLDING_TYPE]
        quantity = call.data[CONF_QUANTITY]
        buy_price = call.data[CONF_BUY_PRICE]

        # Get all config entries
        for entry_id, data in hass.data.get(DOMAIN, {}).items():
            if isinstance(data, dict) and "api_client" in data:
                api_client = data["api_client"]
                
                # Add holding
                api_client.holdings.append({
                    CONF_SYMBOL: symbol,
                    CONF_HOLDING_TYPE: holding_type,
                    CONF_QUANTITY: quantity,
                    CONF_BUY_PRICE: buy_price,
                })
                
                # Force update
                coordinator = data["coordinator"]
                await coordinator.async_request_refresh()
                
                _LOGGER.info(f"Added holding: {symbol}")
                break

    async def async_handle_remove_holding(call: ServiceCall) -> None:
        """Handle remove holding service call."""
        symbol = call.data[CONF_SYMBOL]

        for entry_id, data in hass.data.get(DOMAIN, {}).items():
            if isinstance(data, dict) and "api_client" in data:
                api_client = data["api_client"]
                
                # Remove holding
                api_client.holdings = [
                    h for h in api_client.holdings
                    if h.get(CONF_SYMBOL) != symbol
                ]
                
                # Force update
                coordinator = data["coordinator"]
                await coordinator.async_request_refresh()
                
                _LOGGER.info(f"Removed holding: {symbol}")
                break

    async def async_handle_update_holding(call: ServiceCall) -> None:
        """Handle update holding service call."""
        symbol = call.data[CONF_SYMBOL]
        quantity = call.data.get(CONF_QUANTITY)
        buy_price = call.data.get(CONF_BUY_PRICE)

        for entry_id, data in hass.data.get(DOMAIN, {}).items():
            if isinstance(data, dict) and "api_client" in data:
                api_client = data["api_client"]
                
                # Update holding
                for holding in api_client.holdings:
                    if holding.get(CONF_SYMBOL) == symbol:
                        if quantity is not None:
                            holding[CONF_QUANTITY] = quantity
                        if buy_price is not None:
                            holding[CONF_BUY_PRICE] = buy_price
                        break
                
                # Force update
                coordinator = data["coordinator"]
                await coordinator.async_request_refresh()
                
                _LOGGER.info(f"Updated holding: {symbol}")
                break

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_HOLDING,
        async_handle_add_holding,
        schema=ADD_HOLDING_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_HOLDING,
        async_handle_remove_holding,
        schema=REMOVE_HOLDING_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_HOLDING,
        async_handle_update_holding,
        schema=UPDATE_HOLDING_SCHEMA,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services."""
    hass.services.async_remove(DOMAIN, SERVICE_ADD_HOLDING)
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_HOLDING)
    hass.services.async_remove(DOMAIN, SERVICE_UPDATE_HOLDING)

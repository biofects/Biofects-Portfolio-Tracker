"""
Biofects Portfolio Tracker Integration for Home Assistant.

Tracks stocks, cryptocurrencies, and portfolio performance in real time
using Finnhub and CoinGecko APIs.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import PortfolioAPIClient
from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Biofects Portfolio from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get configuration
    update_interval = entry.options.get(
        CONF_UPDATE_INTERVAL,
        entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    )

    # Initialize API client
    api_client = PortfolioAPIClient(
        finnhub_api_key=entry.data.get("finnhub_api_key"),
        coingecko_api_key=None,  # CoinGecko is free, no key needed
        holdings=entry.data.get("holdings", [])
    )

    # Create coordinator for updates
    coordinator = PortfolioDataUpdateCoordinator(
        hass,
        api_client=api_client,
        update_interval=timedelta(minutes=update_interval),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api_client": api_client,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class PortfolioDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching portfolio data from APIs."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: PortfolioAPIClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        self.api_client = api_client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            return await self.hass.async_add_executor_job(
                self.api_client.update_all
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

"""
Biofects Portfolio Tracker Integration for Home Assistant.

Tracks stocks, cryptocurrencies, and portfolio performance in real time
using Finnhub and CoinGecko APIs.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import PortfolioAPIClient
from .const import DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Biofects Portfolio Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Check for duplicate setup attempts - be more aggressive about preventing conflicts
    if entry.entry_id in hass.data[DOMAIN]:
        _LOGGER.warning("Config entry already exists, cleaning up before re-setup")
        # Force cleanup of existing data
        try:
            await async_unload_entry(hass, entry)
        except Exception as e:
            _LOGGER.debug(f"Cleanup during re-setup failed (expected): {e}")
        # Clear the entry from our data
        hass.data[DOMAIN].pop(entry.entry_id, None)

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
        entry,
        api_client=api_client,
        update_interval=timedelta(minutes=update_interval),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Clean up orphaned entities
    await _cleanup_orphaned_entities(hass, entry, coordinator)

    # Store coordinator and client
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
    # Prevent reload loops during service calls
    if hass.data.get(DOMAIN, {}).get("_updating", False):
        _LOGGER.debug("Skipping reload during update operation")
        return
    
    # Set update flag to prevent concurrent reloads
    hass.data[DOMAIN]["_updating"] = True
    
    try:
        # More robust reload handling - try unload first, handle errors gracefully
        try:
            await async_unload_entry(hass, entry)
        except Exception as unload_err:
            _LOGGER.debug(f"Unload during reload failed (this can be normal): {unload_err}")
        
        # Give a short delay for cleanup
        await asyncio.sleep(0.1)
        
        # Always try the setup, even if unload failed
        await async_setup_entry(hass, entry)
        
    except Exception as err:
        _LOGGER.error(f"Reload failed: {err}")
        # Try to recover by just refreshing data if entry exists
        if entry.entry_id in hass.data.get(DOMAIN, {}):
            _LOGGER.info("Attempting data refresh instead of full reload")
            coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
            api_client = hass.data[DOMAIN][entry.entry_id]["api_client"]
            # Update API client with new holdings
            api_client.holdings = entry.data.get("holdings", [])
            # Request a data refresh
            await coordinator.async_request_refresh()
    finally:
        # Always clear the update flag
        hass.data[DOMAIN]["_updating"] = False


class PortfolioDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching portfolio data from APIs."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
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
            config_entry=config_entry,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            return await self.hass.async_add_executor_job(
                self.api_client.update_all
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


async def _cleanup_orphaned_entities(hass: HomeAssistant, entry: ConfigEntry, coordinator) -> None:
    """Clean up entities that no longer exist in the configuration."""
    entity_registry = async_get_entity_registry(hass)
    
    # Get current holdings from coordinator data
    current_holdings = coordinator.data.get("holdings", []) if coordinator.data else []
    current_lot_ids = set()
    
    # Build set of expected unique_ids
    expected_unique_ids = {
        f"{entry.entry_id}_portfolio_summary",
        f"{entry.entry_id}_portfolio_news",
    }
    
    # Add expected unique_ids for current holdings
    for holding in current_holdings:
        lot_id = f"{holding['symbol']}_{holding.get('lot_id', 0)}"
        expected_unique_ids.add(f"{entry.entry_id}_holding_{lot_id}")
        expected_unique_ids.add(f"{entry.entry_id}_price_{lot_id}")
    
    # Find orphaned entities
    entities_to_remove = []
    for entity_id, entity_entry in entity_registry.entities.items():
        if (entity_entry.platform == DOMAIN and 
            entity_entry.config_entry_id == entry.entry_id and
            entity_entry.unique_id not in expected_unique_ids):
            
            entities_to_remove.append((entity_id, entity_entry.unique_id))
    
    # Remove orphaned entities
    for entity_id, unique_id in entities_to_remove:
        _LOGGER.info(f"Removing orphaned entity: {entity_id} (unique_id: {unique_id})")
        entity_registry.async_remove(entity_id)

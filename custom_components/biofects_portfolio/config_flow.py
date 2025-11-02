"""Config flow for Biofects Portfolio Tracker integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .api_client import PortfolioAPIClient
from .const import (
    CONF_BUY_PRICE,
    CONF_COINGECKO_API_KEY,
    CONF_FINNHUB_API_KEY,
    CONF_HOLDING_TYPE,
    CONF_HOLDINGS,
    CONF_QUANTITY,
    CONF_SYMBOL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    HOLDING_TYPE_CRYPTO,
    HOLDING_TYPE_STOCK,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_FINNHUB_API_KEY): cv.string,
    }
)


class BiofectsPortfolioConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Biofects Portfolio Tracker."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._holdings: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Test API connection
            api_client = PortfolioAPIClient(
                finnhub_api_key=user_input[CONF_FINNHUB_API_KEY],
                coingecko_api_key=None,  # CoinGecko is free, no key needed
            )

            try:
                await self.hass.async_add_executor_job(api_client.test_connection)
            except Exception as err:
                _LOGGER.error(f"Error testing API connection: {err}")
                errors["base"] = "cannot_connect"
            else:
                self._data = user_input
                return await self.async_step_holdings()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_holdings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle adding holdings."""
        if user_input is not None:
            if user_input.get("add_another"):
                # Add the holding
                self._holdings.append({
                    CONF_SYMBOL: user_input[CONF_SYMBOL],
                    CONF_HOLDING_TYPE: user_input[CONF_HOLDING_TYPE],
                    CONF_QUANTITY: user_input[CONF_QUANTITY],
                    CONF_BUY_PRICE: user_input[CONF_BUY_PRICE],
                })
                # Show form again to add another
                return await self.async_step_holdings()
            else:
                # Add final holding if provided
                if user_input.get(CONF_SYMBOL):
                    self._holdings.append({
                        CONF_SYMBOL: user_input[CONF_SYMBOL],
                        CONF_HOLDING_TYPE: user_input[CONF_HOLDING_TYPE],
                        CONF_QUANTITY: user_input[CONF_QUANTITY],
                        CONF_BUY_PRICE: user_input[CONF_BUY_PRICE],
                    })
                
                # Finish configuration
                self._data[CONF_HOLDINGS] = self._holdings
                self._data[CONF_UPDATE_INTERVAL] = DEFAULT_UPDATE_INTERVAL
                
                return self.async_create_entry(
                    title="Biofects Portfolio",
                    data=self._data,
                )

        holdings_schema = vol.Schema({
            vol.Required(CONF_SYMBOL): cv.string,
            vol.Required(CONF_HOLDING_TYPE, default=HOLDING_TYPE_STOCK): vol.In(
                [HOLDING_TYPE_STOCK, HOLDING_TYPE_CRYPTO]
            ),
            vol.Required(CONF_QUANTITY): vol.Coerce(float),
            vol.Required(CONF_BUY_PRICE): vol.Coerce(float),
            vol.Optional("add_another", default=True): cv.boolean,
        })

        return self.async_show_form(
            step_id="holdings",
            data_schema=holdings_schema,
            description_placeholders={
                "holdings_count": str(len(self._holdings)),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> BiofectsPortfolioOptionsFlow:
        """Get the options flow for this handler."""
        return BiofectsPortfolioOptionsFlow(config_entry)


class BiofectsPortfolioOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._current_holdings = list(config_entry.data.get(CONF_HOLDINGS, []))

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - main menu."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "update_interval":
                return await self.async_step_update_interval()
            elif action == "update_api_keys":
                return await self.async_step_update_api_keys()
            elif action == "add_holding":
                return await self.async_step_add_holding()
            elif action == "remove_holding":
                return await self.async_step_remove_holding()
            elif action == "view_holdings":
                return await self.async_step_view_holdings()

        # Show main menu
        holdings_count = len(self._current_holdings)
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action"): vol.In({
                    "update_interval": f"Update refresh interval (currently {self.config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)} min)",
                    "update_api_keys": "Update Finnhub API key",
                    "add_holding": f"Add new holding (currently {holdings_count} holdings)",
                    "remove_holding": f"Remove holding",
                    "view_holdings": f"View all {holdings_count} holdings",
                }),
            }),
            description_placeholders={
                "holdings_count": str(holdings_count),
            },
        )

    async def async_step_update_interval(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Update refresh interval settings."""
        if user_input is not None:
            return self.async_create_entry(title="", data={CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL]})

        return self.async_show_form(
            step_id="update_interval",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                }
            ),
        )

    async def async_step_update_api_keys(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Update Finnhub API key."""
        if user_input is not None:
            # Update config entry data
            new_data = {**self.config_entry.data}
            
            if user_input.get(CONF_FINNHUB_API_KEY):
                new_data[CONF_FINNHUB_API_KEY] = user_input[CONF_FINNHUB_API_KEY]
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data={})

        current_finnhub = self.config_entry.data.get(CONF_FINNHUB_API_KEY, "")

        return self.async_show_form(
            step_id="update_api_keys",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_FINNHUB_API_KEY,
                        default=current_finnhub,
                    ): cv.string,
                }
            ),
            description_placeholders={
                "current_finnhub": current_finnhub[:10] + "..." if current_finnhub else "Not set",
            },
        )

    async def async_step_add_holding(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new holding."""
        if user_input is not None:
            # Get current holdings
            current_holdings = list(self.config_entry.data.get(CONF_HOLDINGS, []))
            
            # Add new holding (normalize symbol to uppercase)
            current_holdings.append({
                CONF_SYMBOL: user_input[CONF_SYMBOL].upper(),
                CONF_HOLDING_TYPE: user_input[CONF_HOLDING_TYPE],
                CONF_QUANTITY: user_input[CONF_QUANTITY],
                CONF_BUY_PRICE: user_input[CONF_BUY_PRICE],
            })
            
            # Update config entry
            new_data = {**self.config_entry.data}
            new_data[CONF_HOLDINGS] = current_holdings
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="add_holding",
            data_schema=vol.Schema({
                vol.Required(CONF_SYMBOL): cv.string,
                vol.Required(CONF_HOLDING_TYPE, default=HOLDING_TYPE_STOCK): vol.In(
                    [HOLDING_TYPE_STOCK, HOLDING_TYPE_CRYPTO]
                ),
                vol.Required(CONF_QUANTITY): vol.Coerce(float),
                vol.Required(CONF_BUY_PRICE): vol.Coerce(float),
            }),
        )

    async def async_step_remove_holding(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Remove a holding."""
        current_holdings = self.config_entry.data.get(CONF_HOLDINGS, [])
        
        if not current_holdings:
            return self.async_abort(reason="no_holdings")
        
        if user_input is not None:
            symbol_to_remove = user_input["holding_to_remove"]
            
            # Remove the holding
            new_holdings = [
                h for h in current_holdings
                if h.get(CONF_SYMBOL) != symbol_to_remove
            ]
            
            # Update config entry
            new_data = {**self.config_entry.data}
            new_data[CONF_HOLDINGS] = new_holdings
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data={})

        # Build list of holdings to choose from
        holdings_list = {
            h.get(CONF_SYMBOL): f"{h.get(CONF_SYMBOL)} ({h.get(CONF_HOLDING_TYPE)})"
            for h in current_holdings
        }

        return self.async_show_form(
            step_id="remove_holding",
            data_schema=vol.Schema({
                vol.Required("holding_to_remove"): vol.In(holdings_list),
            }),
        )

    async def async_step_view_holdings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """View current holdings."""
        holdings = self.config_entry.data.get(CONF_HOLDINGS, [])
        
        if not holdings:
            holdings_text = "No holdings configured."
        else:
            holdings_text = "\n\n".join([
                f"**{h.get(CONF_SYMBOL)}** ({h.get(CONF_HOLDING_TYPE)})\n"
                f"Quantity: {h.get(CONF_QUANTITY)}\n"
                f"Buy Price: ${h.get(CONF_BUY_PRICE)}"
                for h in holdings
            ])

        return self.async_show_form(
            step_id="view_holdings",
            description_placeholders={"holdings_list": holdings_text},
        )

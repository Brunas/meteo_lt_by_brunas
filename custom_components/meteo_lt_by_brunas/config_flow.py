"""config_flow.py"""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, MANUFACTURER


@config_entries.HANDLERS.register(DOMAIN)
class MeteoLtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meteo.Lt."""

    VERSION = 1

    @callback
    def _show_config_form(self, step_id, user_input=None, errors=None):
        """Show the configuration form."""
        step_id = step_id or "user"
        user_input = user_input or {}

        # Prepare default location from user_input or HA config
        default_location = {
            "latitude": user_input.get("latitude", self.hass.config.latitude),
            "longitude": user_input.get("longitude", self.hass.config.longitude),
        }

        data_schema = vol.Schema(
            {
                vol.Required(
                    "location",
                    default=default_location,
                ): selector.LocationSelector(),
            }
        )
        return self.async_show_form(
            step_id=step_id,
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"name": MANUFACTURER},
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Extract latitude and longitude from location selector
            location = user_input.get("location", {})
            latitude = location.get("latitude")
            longitude = location.get("longitude")

            # Store as flat latitude/longitude for backward compatibility
            config_data = {
                "latitude": latitude,
                "longitude": longitude,
            }

            await self.async_set_unique_id(f"{DOMAIN}-{latitude}-{longitude}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=MANUFACTURER, data=config_data)
        return self._show_config_form("user", user_input, errors)

    async def async_step_reconfigure(self, user_input=None) -> FlowResult:
        """Handle the reconfiguration step."""
        errors = {}

        if user_input is not None:
            entry_id = self.context["entry_id"]
            entry = self.hass.config_entries.async_get_entry(entry_id)
            if entry:
                # Extract latitude and longitude from location selector
                location = user_input.get("location", {})
                latitude = location.get("latitude")
                longitude = location.get("longitude")

                # Store as flat latitude/longitude for backward compatibility
                new_data = {
                    "latitude": latitude,
                    "longitude": longitude,
                }

                self.hass.config_entries.async_update_entry(entry, data=new_data)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")
            errors["base"] = "cannot_connect"

        entry_id = self.context["entry_id"]
        entry = self.hass.config_entries.async_get_entry(entry_id)
        if entry:
            current_config = entry.data
            default_latitude = current_config.get("latitude", self.hass.config.latitude)
            default_longitude = current_config.get("longitude", self.hass.config.longitude)
        else:
            default_latitude = self.hass.config.latitude
            default_longitude = self.hass.config.longitude

        return self._show_config_form(
            "reconfigure",
            {"latitude": default_latitude, "longitude": default_longitude},
            errors,
        )

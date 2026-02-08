"""config_flow.py"""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

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
        data_schema = vol.Schema(
            {
                vol.Required(
                    "latitude",
                    default=user_input.get("latitude", self.hass.config.latitude),
                ): vol.Coerce(float),
                vol.Required(
                    "longitude",
                    default=user_input.get("longitude", self.hass.config.longitude),
                ): vol.Coerce(float),
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
            await self.async_set_unique_id(f"{DOMAIN}-{user_input['latitude']}-{user_input['longitude']}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=MANUFACTURER, data=user_input)
        return self._show_config_form("user", user_input, errors)

    async def async_step_reconfigure(self, user_input=None) -> FlowResult:
        """Handle the reconfiguration step."""
        errors = {}

        if user_input is not None:
            entry_id = self.context["entry_id"]
            entry = self.hass.config_entries.async_get_entry(entry_id)
            if entry:
                new_data = dict(entry.data)
                new_data.update(user_input)
                self.hass.config_entries.async_update_entry(entry, data=new_data)
                return self.async_create_entry(title=MANUFACTURER, data=new_data)
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

    async def async_step_reconfigure_confirm(self, user_input=None) -> FlowResult:
        """Handle confirmation of reconfiguration."""
        if user_input is not None:
            return await self.async_step_reconfigure()

        return self._show_config_form("reconfigure_confirm")

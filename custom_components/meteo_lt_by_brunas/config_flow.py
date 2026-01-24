"""config_flow.py"""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, MANUFACTURER, CONF_HYDRO_STATION_CODE, CONF_HYDRO_ENABLE, LOGGER


@config_entries.HANDLERS.register(DOMAIN)
class MeteoLtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meteo.Lt."""

    VERSION = 1
    hydro_stations = []

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
                vol.Optional(CONF_HYDRO_ENABLE, default=user_input.get(CONF_HYDRO_ENABLE, False)): bool,
            }
        )
        return self.async_show_form(
            step_id=step_id,
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"name": MANUFACTURER},
        )

    @callback
    def _show_hydro_form(self, step_id="hydro_select", user_input=None, errors=None):
        """Show hydro station selection form."""
        user_input = user_input or {}
        hydro_dict = {station.code: f"{station.name} ({station.water_body})" for station in self.hydro_stations}

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_HYDRO_STATION_CODE,
                    default=user_input.get(CONF_HYDRO_STATION_CODE),
                ): vol.In(hydro_dict) if hydro_dict else str,
            }
        )
        return self.async_show_form(
            step_id=step_id,
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"station_count": len(self.hydro_stations)},
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{DOMAIN}-{user_input['latitude']}-{user_input['longitude']}"
            )
            self._abort_if_unique_id_configured()

            # If hydro is enabled, go to hydro selection step
            if user_input.get(CONF_HYDRO_ENABLE):
                self.hydro_stations_data = user_input
                return await self.async_step_hydro_select()

            return self.async_create_entry(title=MANUFACTURER, data=user_input)
        return self._show_config_form("user", user_input, errors)

    async def async_step_hydro_select(self, user_input=None):
        """Handle hydro station selection step."""
        errors = {}

        if user_input is not None:
            # Combine weather and hydro data
            config_data = {
                **getattr(self, 'hydro_stations_data', {}),
                CONF_HYDRO_STATION_CODE: user_input.get(CONF_HYDRO_STATION_CODE),
            }
            return self.async_create_entry(title=MANUFACTURER, data=config_data)

        # Fetch hydro stations on first visit
        if not self.hydro_stations:
            try:
                from homeassistant.helpers.aiohttp_client import async_get_clientsession
                from .hydro_api import HydroLtAPI

                # Get Home Assistant's session
                session = async_get_clientsession(self.hass)
                hydro_api = HydroLtAPI(session)

                # Try to fetch stations
                try:
                    self.hydro_stations = await hydro_api.get_hydro_stations()
                    LOGGER.debug("Fetched %d hydrological stations", len(self.hydro_stations))
                except Exception as e:
                    LOGGER.error("Failed to fetch hydro stations: %s", e)
                    errors["base"] = "cannot_fetch_hydro_stations"
                    return self._show_hydro_form(errors=errors)
            except Exception as e:
                LOGGER.error("Error during hydro setup: %s", e)
                errors["base"] = "cannot_connect"
                return self._show_hydro_form(errors=errors)

        return self._show_hydro_form(user_input=user_input, errors=errors)

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
            default_longitude = current_config.get(
                "longitude", self.hass.config.longitude
            )
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

"""__init__.py"""

from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from meteo_lt import MeteoLtAPI
from .const import DOMAIN, MANUFACTURER, LOGGER
from .coordinator import MeteoLtCoordinator

PLATFORMS: Final = [Platform.WEATHER, Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meteo.Lt from a config entry."""
    LOGGER.info("Setting up %s from config entry", MANUFACTURER)

    hass.data.setdefault(DOMAIN, {})

    api = MeteoLtAPI(session=async_get_clientsession(hass))
    latitude = entry.data.get("latitude", hass.config.latitude)
    longitude = entry.data.get("longitude", hass.config.longitude)
    LOGGER.debug("Configured coordinates: %s, %s", latitude, longitude)

    nearest_place = await api.get_nearest_place(latitude, longitude)
    LOGGER.debug("Nearest place found: %s", nearest_place)

    nearest_hydro_station = await api.get_nearest_hydro_station(latitude, longitude)
    LOGGER.debug("Nearest hydro station found: %s", nearest_hydro_station)

    coordinator = MeteoLtCoordinator(hass, api, nearest_place, nearest_hydro_station)
    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "nearest_place": nearest_place,
        "nearest_hydro_station": nearest_hydro_station,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)

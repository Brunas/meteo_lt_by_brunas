"""__init__.py"""

from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from meteo_lt import MeteoLtAPI
from .const import DOMAIN, MANUFACTURER, LOGGER, CONF_HYDRO_STATION_CODE, CONF_HYDRO_ENABLE
from .coordinator import MeteoLtCoordinator
from .hydro_api import HydroLtAPI
from .hydro_coordinator import HydroCoordinator

PLATFORMS: Final = [Platform.WEATHER, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meteo.Lt from a config entry."""
    LOGGER.info("Setting up %s from config entry", MANUFACTURER)

    hass.data.setdefault(DOMAIN, {})

    api = MeteoLtAPI()
    session = async_get_clientsession(hass)
    latitude = entry.data.get("latitude", hass.config.latitude)
    longitude = entry.data.get("longitude", hass.config.longitude)
    LOGGER.debug("Configured coordinates: %s, %s", latitude, longitude)

    nearest_place = await api.get_nearest_place(latitude, longitude)
    LOGGER.debug("Nearest place found: %s", nearest_place)

    coordinator = MeteoLtCoordinator(hass, api, nearest_place)
    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    data = {
        "api": api,
        "nearest_place": nearest_place,
        "coordinator": coordinator,
    }

    # Set up hydrological station if enabled
    if entry.data.get(CONF_HYDRO_ENABLE):
        try:
            hydro_api = HydroLtAPI(session)
            hydro_station_code = entry.data.get(CONF_HYDRO_STATION_CODE)

            if hydro_station_code:
                hydro_station = await hydro_api.get_hydro_station(hydro_station_code)
                hydro_coordinator = HydroCoordinator(hass, hydro_api, hydro_station)
                await hydro_coordinator.async_config_entry_first_refresh()

                data["hydro_api"] = hydro_api
                data["hydro_station"] = hydro_station
                data["hydro_coordinator"] = hydro_coordinator
                LOGGER.info(
                    "Hydrological station %s (%s) set up successfully",
                    hydro_station.name,
                    hydro_station_code,
                )
            else:
                # Try to auto-detect nearest hydro station
                LOGGER.debug("Auto-detecting nearest hydrological station...")
                hydro_api = HydroLtAPI(session)
                nearest_hydro = await hydro_api.get_nearest_hydro_station(latitude, longitude)

                if nearest_hydro:
                    hydro_coordinator = HydroCoordinator(hass, hydro_api, nearest_hydro)
                    await hydro_coordinator.async_config_entry_first_refresh()

                    data["hydro_api"] = hydro_api
                    data["hydro_station"] = nearest_hydro
                    data["hydro_coordinator"] = hydro_coordinator
                    LOGGER.info(
                        "Auto-detected hydrological station: %s (%s)",
                        nearest_hydro.name,
                        nearest_hydro.code,
                    )
                else:
                    LOGGER.warning("No hydrological stations found near coordinates")
        except Exception as e:
            LOGGER.error("Error setting up hydrological station: %s", e)

    hass.data[DOMAIN][entry.entry_id] = data

    # Set up platforms (includes both weather and sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    platforms_to_unload = list(PLATFORMS)

    # Also unload sensor platform if hydro is set up
    if entry.entry_id in hass.data.get(DOMAIN, {}) and "hydro_coordinator" in hass.data[DOMAIN][entry.entry_id]:
        if Platform.SENSOR not in platforms_to_unload:
            platforms_to_unload.append(Platform.SENSOR)

    return await hass.config_entries.async_unload_platforms(entry, platforms_to_unload)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)

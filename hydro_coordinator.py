"""Hydro coordinator for fetching hydrological data."""

from datetime import datetime, timedelta, timezone
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt

from .const import MANUFACTURER, LOGGER, HYDRO_UPDATE_MINUTES


class HydroCoordinator(DataUpdateCoordinator):
    """Class to manage fetching hydrological data."""

    def __init__(self, hass, hydro_api, hydro_station):
        """Initialize.

        Args:
            hass: Home Assistant instance.
            hydro_api: HydroLtAPI instance.
            hydro_station: HydroStation object.
        """
        self.hydro_api = hydro_api
        self.hydro_station = hydro_station
        self.last_measured_data = None
        self.last_updated = None

        super().__init__(
            hass,
            LOGGER,
            name=f"{MANUFACTURER} Hydro - {hydro_station.name}",
            update_interval=timedelta(minutes=HYDRO_UPDATE_MINUTES),
            always_update=True,
        )

    async def _async_update_data(self):
        """Fetch latest measured hydrological data.

        Fetches the latest 24 hours of measured data for the station.
        """
        try:
            data = await self.hydro_api.get_hydro_observation_data(
                self.hydro_station.code,
                observation_type="measured",
                date="latest",
            )

            if data.observations:
                # Get the latest observation
                latest_obs = data.observations[-1]
                self.last_measured_data = latest_obs
                LOGGER.debug(
                    "Hydro data updated for %s: level=%s cm, temp=%s °C",
                    self.hydro_station.name,
                    latest_obs.water_level,
                    latest_obs.water_temperature,
                )
            else:
                LOGGER.warning(
                    "No hydrological observations available for %s",
                    self.hydro_station.name,
                )

            self.last_updated = datetime.now().astimezone(timezone.utc).isoformat()
            return data

        except Exception as e:
            LOGGER.error(
                "Error updating hydrological data for %s: %s",
                self.hydro_station.name,
                e,
            )
            raise

"""coordinator.py"""

import asyncio
from datetime import datetime, timedelta, timezone

import aiohttp
from homeassistant.helpers import sun
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt

from .const import LOGGER, MANUFACTURER, UPDATE_MINUTES


class MeteoLtCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Meteo LT data."""

    def __init__(self, hass, api, nearest_place, nearest_hydro_station):
        """Initialize."""
        self.api = api
        self.nearest_place = nearest_place
        self.nearest_hydro_station = nearest_hydro_station
        self.hydro_observations = None
        self.last_updated = None
        self._hydro_failure_logged = False
        super().__init__(
            hass,
            LOGGER,
            name=MANUFACTURER,
            update_interval=timedelta(minutes=UPDATE_MINUTES),
            always_update=True,
        )

    def _map_condition(self, condition_code, forecast_time_utc):
        """Map API weather condition to HA condition."""
        is_day = sun.is_up(self.hass, forecast_time_utc)
        condition_mapping = {
            "clear": "sunny" if is_day else "clear-night",
            "partly-cloudy": "partlycloudy",
            "cloudy-with-sunny-intervals": "partlycloudy",
            "cloudy": "cloudy",
            "thunder": "lightning",
            "isolated-thunderstorms": "lightning-rainy",
            "thunderstorms": "lightning-rainy",
            "heavy-rain-with-thunderstorms": "lightning-rainy",
            "light-rain": "rainy",
            "rain": "rainy",
            "heavy-rain": "pouring",
            "light-sleet": "snowy-rainy",
            "sleet": "snowy-rainy",
            "freezing-rain": "snowy-rainy",
            "hail": "hail",
            "light-snow": "snowy",
            "snow": "snowy",
            "heavy-snow": "snowy",
            "fog": "fog",
            None: "exceptional",
        }
        return condition_mapping.get(condition_code, "exceptional")

    async def _fetch_forecast(self):
        """Fetch the forecast, logging every failure with its reason."""
        try:
            return await self.api.get_forecast(self.nearest_place.code)
        except asyncio.CancelledError:
            # Home Assistant marks every entity of a coordinator unavailable when an
            # update is cancelled, but logs nothing at all - log it here so a blip is
            # not completely invisible. Cancellation during shutdown is expected.
            if self.hass.is_stopping:
                LOGGER.debug("Fetching %s data was cancelled during shutdown", MANUFACTURER)
            else:
                LOGGER.warning(
                    "Fetching %s data was cancelled, entities stay unavailable until the next update",
                    MANUFACTURER,
                )
            raise
        except (TimeoutError, aiohttp.ClientError) as exc:
            raise UpdateFailed(f"Error communicating with meteo.lt API: {exc!r}") from exc

    def _resolve_current_conditions(self, forecast):
        """Make sure current conditions are set, warning when they have to be guessed.

        The API occasionally returns a forecast that does not contain an entry for the
        current hour. Without a fallback every sensor raises while rendering its state,
        which surfaces as entities keeping stale values or failing to load at all.
        """
        if forecast.current_conditions:
            return

        forecast.current_conditions = forecast.forecast_timestamps[0]
        LOGGER.warning(
            "No %s forecast for the current hour (created %s), falling back to the nearest forecast at %s",
            MANUFACTURER,
            forecast.forecast_created,
            forecast.current_conditions.datetime,
        )

    async def _fetch_hydro_observations(self):
        """Fetch hydro observations, best-effort but never silently."""
        if not self.nearest_hydro_station:
            return None

        try:
            hydro_observations = await self.api.get_hydro_observation_data(self.nearest_hydro_station.code)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - best-effort fetch; pylint: disable=broad-except
            # Only the first failure of a streak is logged as a warning to avoid
            # flooding the log when the hydro station is unavailable for a long time.
            if self._hydro_failure_logged:
                LOGGER.debug("Failed to fetch hydro observations for %s: %r", self.nearest_hydro_station.code, exc)
            else:
                LOGGER.warning(
                    "Failed to fetch hydro observations for %s, hydro sensors have no value: %r",
                    self.nearest_hydro_station.code,
                    exc,
                )
                self._hydro_failure_logged = True
            return None

        if self._hydro_failure_logged:
            LOGGER.info("Fetching %s hydro observations recovered", MANUFACTURER)
            self._hydro_failure_logged = False

        LOGGER.debug("Hydro data fetched: %s", hydro_observations)
        return hydro_observations

    async def _async_update_data(self):
        """Fetch data from API."""
        forecast = await self._fetch_forecast()

        if forecast is None or not forecast.forecast_timestamps:
            raise UpdateFailed("meteo.lt returned a forecast without any forecast timestamps")

        self._resolve_current_conditions(forecast)

        forecast_time_utc = dt.parse_datetime(forecast.current_conditions.datetime)
        forecast.current_conditions.condition = self._map_condition(
            forecast.current_conditions.condition_code, forecast_time_utc
        )

        for timestamp in forecast.forecast_timestamps:
            forecast_time_utc = dt.parse_datetime(timestamp.datetime)
            timestamp.condition = self._map_condition(timestamp.condition_code, forecast_time_utc)

        # Fetch hydro observation data for nearest hydro station if available
        self.hydro_observations = await self._fetch_hydro_observations()

        LOGGER.debug("Forecast calculated: %s", forecast)
        self.last_updated = datetime.now().astimezone(timezone.utc).isoformat()
        return forecast

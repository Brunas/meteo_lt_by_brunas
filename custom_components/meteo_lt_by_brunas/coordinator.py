"""coordinator.py"""

from datetime import datetime, timedelta, timezone
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers import sun
from homeassistant.util import dt

from .const import MANUFACTURER, LOGGER, UPDATE_MINUTES


class MeteoLtCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Meteo LT data."""

    def __init__(self, hass, api, nearest_place, nearest_hydro_station):
        """Initialize."""
        self.api = api
        self.nearest_place = nearest_place
        self.nearest_hydro_station = nearest_hydro_station
        self.last_updated = None
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

    async def _async_update_data(self):
        """Fetch data from API."""
        forecast = await self.api.get_forecast(self.nearest_place.code)

        if forecast.current_conditions:
            forecast_time_utc = dt.parse_datetime(forecast.current_conditions.datetime)
            forecast.current_conditions.condition = self._map_condition(
                forecast.current_conditions.condition_code,
                forecast_time_utc
            )

        for timestamp in forecast.forecast_timestamps:
            forecast_time_utc = dt.parse_datetime(timestamp.datetime)
            timestamp.condition = self._map_condition(
                timestamp.condition_code,
                forecast_time_utc
            )

        LOGGER.debug("Forecast calculated: %s", forecast)
        self.last_updated = datetime.now().astimezone(timezone.utc).isoformat()
        return forecast
"""weather.py"""

# pylint: disable=unused-argument, abstract-method, too-many-ancestors

from typing import List
from homeassistant.components.weather import (
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfPrecipitationDepth,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from .const import DOMAIN, MANUFACTURER, LOGGER
from .coordinator import MeteoLtCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Meteo.Lt weather based on a config entry."""
    LOGGER.debug(
        "Weather setting up input: hass.data - %s, config entry - %s",
        hass.data[DOMAIN][entry.entry_id],
        entry,
    )
    async_add_entities(
        [
            MeteoLtWeather(
                hass.data[DOMAIN][entry.entry_id]["coordinator"],
                hass.data[DOMAIN][entry.entry_id]["nearest_place"],
                entry,
            )
        ],
        True,
    )


class MeteoLtWeather(SingleCoordinatorWeatherEntity[MeteoLtCoordinator]):
    """Meteo.lt WeatherEntity implementation"""

    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND

    def __init__(self, coordinator, nearest_place, config_entry):
        """__init__"""
        super().__init__(coordinator)
        self._attr_name = f"{config_entry.title} {nearest_place.name}"
        self._attr_unique_id = config_entry.entry_id
        self._attr_device_info = {
            "entry_type": DeviceEntryType.SERVICE,
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": self._attr_name,
            "manufacturer": MANUFACTURER,
        }

    @property
    def native_temperature(self):
        """Native temperature"""
        return self.coordinator.data.forecast_timestamps[0].temperature

    @property
    def native_temperature_unit(self):
        """Native temperature unit"""
        return UnitOfTemperature.CELSIUS

    @property
    def humidity(self):
        """Humidity"""
        return self.coordinator.data.forecast_timestamps[0].humidity

    @property
    def native_wind_speed(self):
        """Native wind speed"""
        return self.coordinator.data.forecast_timestamps[0].wind_speed

    @property
    def native_wind_speed_unit(self):
        """Native wind speed unit"""
        return UnitOfSpeed.METERS_PER_SECOND

    @property
    def wind_bearing(self):
        """Native wind bearing"""
        return self.coordinator.data.forecast_timestamps[0].wind_bearing

    @property
    def native_pressure(self):
        """Native pressure"""
        return self.coordinator.data.forecast_timestamps[0].pressure

    @property
    def native_pressure_unit(self):
        """Native pressure unit"""
        return UnitOfPressure.HPA

    @property
    def native_precipitation(self):
        """Native precipitation"""
        return self.coordinator.data.forecast_timestamps[0].precipitation

    @property
    def native_precipitation_unit(self):
        """Native precipitation unit"""
        return UnitOfPrecipitationDepth.MILLIMETERS

    @property
    def condition(self):
        """Condition"""
        return self.coordinator.data.forecast_timestamps[0].condition

    @property
    def cloud_coverage(self):
        """Cloud coverage"""
        return self.coordinator.data.forecast_timestamps[0].cloud_coverage

    @property
    def native_apparent_temperature(self):
        """Native apparent temperature"""
        return self.coordinator.data.forecast_timestamps[0].apparent_temperature

    @property
    def native_wind_gust_speed(self):
        """Native wind gust speed"""
        return self.coordinator.data.forecast_timestamps[0].wind_gust_speed

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return WeatherEntityFeature.FORECAST_HOURLY

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        return {
            "last_updated": self.coordinator.last_updated,
            "forecast_created": self.coordinator.data.forecast_created,
        }

    @callback
    def _async_forecast_hourly(self) -> List[Forecast] | None:
        """Return the hourly forecast in native units."""
        if not self.supported_features & WeatherEntityFeature.FORECAST_HOURLY:
            return None

        hourly_forecast = [
            Forecast(
                datetime=entry.datetime,
                native_temperature=entry.temperature,
                native_apparent_temperature=entry.apparent_temperature,
                native_wind_speed=entry.wind_speed,
                native_wind_gust_speed=entry.wind_gust_speed,
                wind_bearing=entry.wind_bearing,
                cloud_coverage=entry.cloud_coverage,
                native_pressure=entry.pressure,
                humidity=entry.humidity,
                native_precipitation=entry.precipitation,
                condition=entry.condition,
            )
            for entry in self.coordinator.data.forecast_timestamps
        ]
        LOGGER.debug("Hourly_forecast created: %s", hourly_forecast)
        return hourly_forecast

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Handling Meteo.Lt weather coordinator update for entity %s", self.entity_id)
        self.async_write_ha_state()

    async def async_update(self):
        """Refreshing coordinator"""
        LOGGER.debug("Updating Meteo.Lt weather entity %s", self.entity_id)
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.async_add_listener(self._handle_coordinator_update))

"""sensor.py"""

# pylint: disable=too-many-arguments

from typing import Dict, Any
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfPrecipitationDepth,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, LOGGER, MANUFACTURER


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Meteo.Lt sensor based on a config entry."""
    LOGGER.debug(
        "Sensor setting up input: hass.data - %s, config entry - %s",
        hass.data[DOMAIN][entry.entry_id],
        entry,
    )

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    nearest_place = hass.data[DOMAIN][entry.entry_id]["nearest_place"]

    sensors = [
        MeteoLtCurrentConditionsSensor(coordinator, nearest_place, entry),
        MeteoLtTemperatureSensor(coordinator, nearest_place, entry),
        MeteoLtApparentTemperatureSensor(coordinator, nearest_place, entry),
        MeteoLtWindSpeedSensor(coordinator, nearest_place, entry),
        MeteoLtWindGustSpeedSensor(coordinator, nearest_place, entry),
        MeteoLtWindBearingSensor(coordinator, nearest_place, entry),
        MeteoLtCloudCoverageSensor(coordinator, nearest_place, entry),
        MeteoLtPressureSensor(coordinator, nearest_place, entry),
        MeteoLtHumiditySensor(coordinator, nearest_place, entry),
        MeteoLtPrecipitationSensor(coordinator, nearest_place, entry),
        MeteoLtConditionSensor(coordinator, nearest_place, entry),
    ]

    # Add hydro sensors if hydrological station is configured
    domain_data = hass.data[DOMAIN][entry.entry_id]
    if "hydro_coordinator" in domain_data and "hydro_station" in domain_data:
        hydro_coordinator = domain_data["hydro_coordinator"]
        hydro_station = domain_data["hydro_station"]
        LOGGER.debug("Adding hydro sensors for station: %s", hydro_station.name)

        sensors.extend([
            HydroWaterLevelSensor(hydro_coordinator, hydro_station, entry),
            HydroWaterTemperatureSensor(hydro_coordinator, hydro_station, entry),
        ])

    async_add_entities(sensors)


class MeteoLtBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for all Meteo.Lt sensors."""

    def __init__(
        self,
        coordinator,
        nearest_place,
        config_entry,
        attribute,
        device_class=None,
        state_class=None,
        unit=None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{config_entry.title} {nearest_place.name} {attribute.replace('_', ' ').title()}"
        self._attr_unique_id = f"{config_entry.entry_id}-{attribute}".replace(
            " ", "_"
        ).lower()
        self._attribute = attribute
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.title,
            "manufacturer": MANUFACTURER,
        }

    @property
    def native_value(self):
        """Return the value of the sensor."""
        try:
            value = getattr(self.coordinator.data.current_conditions, self._attribute)
            return value
        except AttributeError:
            # Handle cases where the attribute doesn't exist on the object
            LOGGER.debug(
                "Attribute %s not found on current_conditions, returning None",
                self._attribute
            )
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any] | None:
        """Return the state attributes."""
        return {
            "last_updated": self.coordinator.last_updated,
            "forecast_created": self.coordinator.data.forecast_created,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug(
            "Handling Meteo.Lt sensor coordinator update for entity %s", self.entity_id
        )
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch new state data for the sensor."""
        LOGGER.debug("Updating Meteo.Lt sensor entity %s", self.entity_id)
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )


class MeteoLtCurrentConditionsSensor(MeteoLtBaseSensor):
    """Representation of a Meteo.Lt Current Conditions Sensor."""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "Current Conditions",
            None,
            None,
            UnitOfTemperature.CELSIUS,
        )
        self._attribute = "temperature"

    @property
    def extra_state_attributes(self) -> Dict[str, Any] | None:
        """Return the state attributes."""
        current_conditions = self.coordinator.data.current_conditions
        LOGGER.debug("Current conditions: %s", current_conditions)

        base_attributes = super().extra_state_attributes or {}
        current_conditions_attributes = {
            "native_temperature": current_conditions.temperature,
            "native_apparent_temperature": current_conditions.apparent_temperature,
            "native_wind_speed": current_conditions.wind_speed,
            "native_wind_gust_speed": current_conditions.wind_gust_speed,
            "wind_bearing": current_conditions.wind_bearing,
            "cloud_coverage": current_conditions.cloud_coverage,
            "native_pressure": current_conditions.pressure,
            "humidity": current_conditions.humidity,
            "native_precipitation": current_conditions.precipitation,
            "condition": current_conditions.condition,
            "native_temperature_unit": UnitOfTemperature.CELSIUS,
            "native_wind_speed_unit": UnitOfSpeed.METERS_PER_SECOND,
            "native_pressure_unit": UnitOfPressure.HPA,
            "native_precipitation_unit": UnitOfPrecipitationDepth.MILLIMETERS,
        }
        return {**current_conditions_attributes, **base_attributes}


class MeteoLtTemperatureSensor(MeteoLtBaseSensor):
    """MeteoLtBaseSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "temperature",
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS,
        )


class MeteoLtApparentTemperatureSensor(MeteoLtBaseSensor):
    """MeteoLtApparentTemperatureSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "apparent_temperature",
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS,
        )


class MeteoLtWindSpeedSensor(MeteoLtBaseSensor):
    """MeteoLtWindSpeedSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "wind_speed",
            SensorDeviceClass.WIND_SPEED,
            SensorStateClass.MEASUREMENT,
            UnitOfSpeed.METERS_PER_SECOND,
        )


class MeteoLtWindGustSpeedSensor(MeteoLtBaseSensor):
    """MeteoLtWindGustSpeedSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "wind_gust_speed",
            SensorDeviceClass.WIND_SPEED,
            SensorStateClass.MEASUREMENT,
            UnitOfSpeed.METERS_PER_SECOND,
        )


class MeteoLtWindBearingSensor(MeteoLtBaseSensor):
    """MeteoLtWindBearingSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "wind_bearing",
            None,  # No degrees or anything specific to wind direction
            SensorStateClass.MEASUREMENT,
            DEGREE,
        )


class MeteoLtCloudCoverageSensor(MeteoLtBaseSensor):
    """MeteoLtCloudCoverageSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "cloud_coverage",
            None,  # No cloud coverage specific device class
            SensorStateClass.MEASUREMENT,
            PERCENTAGE,
        )


class MeteoLtPressureSensor(MeteoLtBaseSensor):
    """MeteoLtPressureSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "pressure",
            SensorDeviceClass.ATMOSPHERIC_PRESSURE,
            SensorStateClass.MEASUREMENT,
            UnitOfPressure.HPA,
        )


class MeteoLtHumiditySensor(MeteoLtBaseSensor):
    """MeteoLtHumiditySensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "humidity",
            SensorDeviceClass.HUMIDITY,
            SensorStateClass.MEASUREMENT,
            PERCENTAGE,
        )


class MeteoLtPrecipitationSensor(MeteoLtBaseSensor):
    """MeteoLtPrecipitationSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        super().__init__(
            coordinator,
            nearest_place,
            config_entry,
            "precipitation",
            SensorDeviceClass.PRECIPITATION,
            SensorStateClass.MEASUREMENT,
            UnitOfPrecipitationDepth.MILLIMETERS,
        )


class MeteoLtConditionSensor(MeteoLtBaseSensor):
    """MeteoLtConditionSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        # Text representation of conditions
        super().__init__(coordinator, nearest_place, config_entry, "condition")


class HydroBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for hydrological sensors."""

    def __init__(
        self,
        coordinator,
        hydro_station,
        config_entry,
        attribute_name,
        device_class=None,
        state_class=None,
        unit_of_measurement=None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.hydro_station = hydro_station
        self._attribute = attribute_name
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_unique_id = f"{config_entry.entry_id}_{hydro_station.code}_{attribute_name}"
        self._attr_name = f"{config_entry.title} {hydro_station.name} {attribute_name.replace('_', ' ').title()}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{config_entry.entry_id}_hydro_{hydro_station.code}")},
            "name": f"{config_entry.title} - {hydro_station.name}",
            "manufacturer": MANUFACTURER,
        }

    @property
    def available(self):
        """Return if entity is available."""
        if not self.coordinator.last_update_success:
            return False
        if not self.coordinator.data or not self.coordinator.data.observations:
            return False
        return len(self.coordinator.data.observations) > 0

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.observations:
            return None

        latest_observation = self.coordinator.data.observations[0]
        return getattr(latest_observation, self._attribute, None)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return entity specific state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs["station_name"] = self.hydro_station.name
            attrs["station_code"] = self.hydro_station.code
            attrs["water_body"] = self.hydro_station.water_body
        return attrs


class HydroWaterLevelSensor(HydroBaseSensor):
    """Water level sensor for hydrological station."""

    def __init__(self, coordinator, hydro_station, config_entry):
        super().__init__(
            coordinator,
            hydro_station,
            config_entry,
            "water_level",
            SensorDeviceClass.DISTANCE,
            SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS,  # Will be cm but HA doesn't have cm for distance
        )
        self._attr_native_unit_of_measurement = "cm"


class HydroWaterTemperatureSensor(HydroBaseSensor):
    """Water temperature sensor for hydrological station."""

    def __init__(self, coordinator, hydro_station, config_entry):
        super().__init__(
            coordinator,
            hydro_station,
            config_entry,
            "water_temperature",
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS,
        )

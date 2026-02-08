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
    UnitOfLength,
)
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, LOGGER


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Meteo.Lt sensor based on a config entry."""
    LOGGER.debug(
        "Sensor setting up input: hass.data - %s, config entry - %s",
        hass.data[DOMAIN][entry.entry_id],
        entry,
    )

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    nearest_place = hass.data[DOMAIN][entry.entry_id]["nearest_place"]
    nearest_hydro_station = hass.data[DOMAIN][entry.entry_id]["nearest_hydro_station"]

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
        MeteoLtWarningsSensor(coordinator, nearest_place, entry),
        MeteoLtWaterLevelSensor(coordinator, nearest_hydro_station, entry),
        MeteoLtWaterTemperatureSensor(coordinator, nearest_hydro_station, entry),
    ]

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
        self._attr_name = f"{config_entry.title} {nearest_place.name} - {attribute}"
        self._attr_unique_id = f"{config_entry.entry_id}-{attribute}".replace(
            " ", "_"
        ).lower()
        self._attribute = attribute
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        """Return the value of the sensor."""
        return getattr(self.coordinator.data.current_conditions, self._attribute)

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
            "warnings": current_conditions.warnings,
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


class MeteoLtWarningsSensor(MeteoLtBaseSensor):
    """MeteoLtWarningsSensor"""

    def __init__(self, coordinator, nearest_place, config_entry):
        # Text representation of warnings
        super().__init__(coordinator, nearest_place, config_entry, "warnings")

    @property
    def native_value(self):
        """Return count of warnings to fit 255-char limit."""
        warnings = getattr(self.coordinator.data.current_conditions, self._attribute)
        if not warnings:
            return 0
        return len(warnings) if isinstance(warnings, list) else 1

    @property
    def extra_state_attributes(self) -> Dict[str, Any] | None:
        """Return detailed warnings in attributes."""
        base_attrs = super().extra_state_attributes or {}
        warnings = getattr(self.coordinator.data.current_conditions, self._attribute)
        if warnings:
            warnings_list = [
                {
                    "administrative_division": w.administrative_division,
                    "category": w.category,
                    "type": w.warning_type,
                    "severity": w.severity,
                    "description": w.description,
                    "instruction": w.instruction,
                    "start": w.start_time,
                    "end": w.end_time,
                }
                for w in (warnings if isinstance(warnings, list) else [warnings])
            ]
            base_attrs["warnings_detail"] = warnings_list
        return base_attrs


class MeteoLtHydroBaseSensor(MeteoLtBaseSensor):
    """Base class for hydro sensors."""

    def __init__(
        self,
        coordinator,
        nearest_hydro_station,
        config_entry,
        attribute,
        device_class=None,
        state_class=None,
        unit=None,
    ):
        """Initialize the hydro sensor."""
        super().__init__(
            coordinator,
            nearest_hydro_station,
            config_entry,
            attribute,
            device_class,
            state_class,
            unit,
        )
        self._observation_attribute = attribute

    def _get_observation_fields(self, obs):
        """Return the fields to include in observation list. Override in subclass."""
        raise NotImplementedError

    @property
    def native_value(self):
        """Return the value from hydro observations if available."""
        hydro = getattr(self.coordinator, "hydro_observations", None)
        if not hydro or not hasattr(hydro, "observations") or not hydro.observations:
            return None
        # Get the latest observation (last item in the list)
        latest_observation = hydro.observations[-1]
        return getattr(latest_observation, self._observation_attribute, None)

    @property
    def extra_state_attributes(self) -> Dict[str, Any] | None:
        """Return all hydro observations in attributes."""
        base_attrs = super().extra_state_attributes or {}
        hydro = getattr(self.coordinator, "hydro_observations", None)
        if hydro:
            # Add station information
            if hasattr(hydro, "station"):
                base_attrs["station_code"] = getattr(hydro.station, "code", None)
                base_attrs["station_name"] = getattr(hydro.station, "name", None)
                base_attrs["water_body"] = getattr(hydro.station, "water_body", None)

            # Add observations as an array
            if hasattr(hydro, "observations") and hydro.observations:
                observations_list = [
                    self._get_observation_fields(obs) for obs in hydro.observations
                ]
                base_attrs["observations"] = observations_list
                base_attrs["observation_count"] = len(observations_list)
        return base_attrs


class MeteoLtWaterLevelSensor(MeteoLtHydroBaseSensor):
    """MeteoLtWaterLevelSensor"""

    def __init__(self, coordinator, nearest_hydro_station, config_entry):
        super().__init__(
            coordinator,
            nearest_hydro_station,
            config_entry,
            "water_level",
            None,
            SensorStateClass.MEASUREMENT,
            UnitOfLength.CENTIMETERS,
        )

    def _get_observation_fields(self, obs):
        """Return water level observation fields."""
        return {
            "datetime": obs.observation_datetime,
            "water_level": obs.water_level,
            "water_discharge": obs.water_discharge,
        }


class MeteoLtWaterTemperatureSensor(MeteoLtHydroBaseSensor):
    """MeteoLtWaterTemperatureSensor"""

    def __init__(self, coordinator, nearest_hydro_station, config_entry):
        super().__init__(
            coordinator,
            nearest_hydro_station,
            config_entry,
            "water_temperature",
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
            UnitOfTemperature.CELSIUS,
        )

    def _get_observation_fields(self, obs):
        """Return water temperature observation fields."""
        return {
            "datetime": obs.observation_datetime,
            "water_temperature": obs.water_temperature,
        }

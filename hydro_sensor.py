"""Hydrological sensors for Meteo.Lt integration."""

from typing import Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength, UnitOfTemperature, UnitOfVolumetricFlux
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity_registry import async_entries_for_config_entry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER, CONF_HYDRO_STATION_CODE


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up hydrological sensors from a config entry.

    Args:
        hass: Home Assistant instance.
        entry: Config entry.
        async_add_entities: Function to add entities.
    """
    LOGGER.debug("Hydro sensor setup for entry: %s", entry.entry_id)

    if entry.entry_id not in hass.data[DOMAIN]:
        LOGGER.warning("No data for entry %s", entry.entry_id)
        return

    coordinator = hass.data[DOMAIN][entry.entry_id].get("hydro_coordinator")
    if not coordinator:
        LOGGER.debug("No hydro coordinator available, skipping hydro sensor setup")
        return

    hydro_station = coordinator.hydro_station

    sensors = [
        HydroWaterLevelSensor(coordinator, hydro_station, entry),
        HydroWaterTemperatureSensor(coordinator, hydro_station, entry),
        HydroWaterDischargeSensor(coordinator, hydro_station, entry),
    ]

    async_add_entities(sensors)
    LOGGER.debug(
        "Added %d hydro sensors for station %s",
        len(sensors),
        hydro_station.name,
    )


class HydroSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for hydrological sensors."""

    def __init__(self, coordinator, hydro_station, config_entry):
        """Initialize sensor.

        Args:
            coordinator: HydroCoordinator instance.
            hydro_station: HydroStation object.
            config_entry: Config entry.
        """
        super().__init__(coordinator)
        self.hydro_station = hydro_station
        self._config_entry = config_entry
        self._attr_has_entity_name = True
        self._attr_should_poll = False

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {
                (DOMAIN, f"hydro-{self.hydro_station.code}")
            },
            "name": f"Hydro Station - {self.hydro_station.name}",
            "manufacturer": "Meteo.Lt",
            "entry_type": DeviceEntryType.SERVICE,
            "model": self.hydro_station.water_body,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class HydroWaterLevelSensor(HydroSensorBase):
    """Water level sensor."""

    _attr_native_unit_of_measurement = UnitOfLength.CENTIMETERS
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_hydro_{self.hydro_station.code}_water_level"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Water Level"

    @property
    def native_value(self) -> Optional[float]:
        """Return the state."""
        if self.coordinator.last_measured_data:
            return self.coordinator.last_measured_data.water_level
        return None

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs["observations_data_range"] = str(
                self.coordinator.data.observations_data_range
            )
        return attrs


class HydroWaterTemperatureSensor(HydroSensorBase):
    """Water temperature sensor."""

    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_hydro_{self.hydro_station.code}_water_temp"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Water Temperature"

    @property
    def native_value(self) -> Optional[float]:
        """Return the state."""
        if self.coordinator.last_measured_data:
            return self.coordinator.last_measured_data.water_temperature
        return None

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "water_body": self.hydro_station.water_body,
        }


class HydroWaterDischargeSensor(HydroSensorBase):
    """Water discharge sensor."""

    _attr_native_unit_of_measurement = UnitOfVolumetricFlux.CUBIC_METERS_PER_SECOND
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{DOMAIN}_hydro_{self.hydro_station.code}_water_discharge"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Water Discharge"

    @property
    def native_value(self) -> Optional[float]:
        """Return the state."""
        if self.coordinator.last_measured_data:
            return self.coordinator.last_measured_data.water_discharge
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Water discharge is not available for measured data, only historical
        return False

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "note": "Water discharge is only available in historical data",
        }

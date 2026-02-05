"""binary_sensor.py"""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, LOGGER


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Meteo.lt binary sensor."""
    LOGGER.debug(
        "Binary sensor setting up input: hass.data - %s, config entry - %s",
        hass.data[DOMAIN][entry.entry_id],
        entry,
    )
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    nearest_place = hass.data[DOMAIN][entry.entry_id]["nearest_place"]

    async_add_entities([MeteoLtAlertSensor(coordinator, nearest_place, entry)], True)


class MeteoLtAlertSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor to track any upcoming weather extremes."""

    def __init__(self, coordinator, nearest_place, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{config_entry.title} {nearest_place.name} - Alerts"
        self._attr_unique_id = f"{config_entry.entry_id}-alerts".replace(" ", "_").lower()
        self._attr_device_class = BinarySensorDeviceClass.SAFETY

    @property
    def is_on(self) -> bool:
        """Return true if any warning exists in the forecast."""
        if not self.coordinator.data or not hasattr(self.coordinator.data, "forecast_timestamps"):
            return False

        for interval in self.coordinator.data.forecast_timestamps:
            if interval.warnings:
                return True
        return False

    @property
    def extra_state_attributes(self):
        """Return all upcoming warnings as list in attributes."""
        alerts = []

        if self.coordinator.data and hasattr(self.coordinator.data, "forecast_timestamps"):
            for forecast in self.coordinator.data.forecast_timestamps:
                if not forecast.warnings or forecast.warnings == "no_warning":
                    continue

                raw_warnings = forecast.warnings
                if not isinstance(raw_warnings, list):
                    raw_warnings = [raw_warnings]

                for w in raw_warnings:
                    if hasattr(w, "warning_type"):
                        alerts.append(
                            {
                                "county": getattr(w, "county", "Unknown"),
                                "type": getattr(w, "warning_type", "Unknown"),
                                "severity": getattr(w, "severity", "Unknown"),
                                "description": getattr(w, "description", ""),
                                "start": getattr(w, "start_time", forecast.datetime),
                                "end": getattr(w, "end_time", None),
                                "forecast_time": forecast.datetime,
                            }
                        )
                    else:
                        alerts.append(
                            {
                                "type": str(w),
                                "forecast_time": forecast.datetime,
                            }
                        )

        return {
            "alerts": alerts,
            "count": len(alerts),
            "last_updated": self.coordinator.last_updated,
            "forecast_created": self.coordinator.data.forecast_created,
        }

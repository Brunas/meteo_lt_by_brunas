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
        self.hass = coordinator.hass

    def _get_valid_warnings(self, interval):
        """Extract valid warning objects from an interval."""
        LOGGER.debug(
            "Checking warnings for interval %s: warnings=%s, type=%s",
            getattr(interval, "datetime", "unknown"),
            interval.warnings,
            type(interval.warnings).__name__,
        )

        if not interval.warnings or interval.warnings == 0:
            LOGGER.debug("No warnings or warnings == 0, returning empty list")
            return []

        raw_warnings = interval.warnings
        if not isinstance(raw_warnings, list):
            raw_warnings = [raw_warnings]

        valid_warnings = [w for w in raw_warnings if hasattr(w, "warning_type")]

        for w in valid_warnings:
            LOGGER.debug(
                "Valid warning: type=%s, severity=%s, has_warning_type=%s",
                getattr(w, "warning_type", "N/A"),
                getattr(w, "severity", "N/A"),
                hasattr(w, "warning_type"),
            )

        return valid_warnings

    @property
    def is_on(self) -> bool:
        """Return true if any warning exists in the forecast."""
        LOGGER.debug("Evaluating is_on for binary sensor %s", self._attr_unique_id)

        if not self.coordinator.data or not hasattr(self.coordinator.data, "forecast_timestamps"):
            return False

        total_intervals = len(self.coordinator.data.forecast_timestamps)

        for idx, interval in enumerate(self.coordinator.data.forecast_timestamps):
            valid_warnings = self._get_valid_warnings(interval)
            if valid_warnings:
                LOGGER.info(
                    "Binary sensor ON: Found %d valid warning(s) in interval %d/%d at %s",
                    len(valid_warnings),
                    idx + 1,
                    total_intervals,
                    getattr(interval, "datetime", "unknown"),
                )
                return True

        return False

    @property
    def extra_state_attributes(self):
        """Return all upcoming warnings as list in attributes."""
        LOGGER.debug("Building extra_state_attributes for binary sensor %s", self._attr_unique_id)
        alerts = []

        if self.coordinator.data and hasattr(self.coordinator.data, "forecast_timestamps"):
            for idx, forecast in enumerate(self.coordinator.data.forecast_timestamps):
                valid_warnings = self._get_valid_warnings(forecast)

                # Get Home Assistant language, default to 'en'
                lang = self.hass.config.language if self.hass.config.language in ["en", "lt"] else "en"

                for w in valid_warnings:
                    alert = {
                        "administrative_division": getattr(w, "administrative_division", "Unknown"),
                        "category": getattr(w, "category", "weather"),
                        "type": getattr(w, "warning_type", "Unknown"),
                        "severity": getattr(w, "severity", "Unknown"),
                        "headline": (
                            w.get_headline(lang) if hasattr(w, "get_headline") else getattr(w, "headline", "")
                        ),
                        "description": (
                            w.get_description(lang) if hasattr(w, "get_description") else getattr(w, "description", "")
                        ),
                        "instruction": (
                            w.get_instruction(lang) if hasattr(w, "get_instruction") else getattr(w, "instruction", "")
                        ),
                        "start": getattr(w, "start_time", forecast.datetime),
                        "end": getattr(w, "end_time", None),
                        "forecast_time": forecast.datetime,
                    }
                    alerts.append(alert)
                    LOGGER.debug(
                        "Alert %d: %s (%s) at %s",
                        len(alerts),
                        alert["type"],
                        alert["severity"],
                        forecast.datetime,
                    )

        LOGGER.info("Binary sensor attributes: %d total alerts", len(alerts))

        return {
            "alerts": alerts,
            "count": len(alerts),
            "last_updated": self.coordinator.last_updated,
            "forecast_created": self.coordinator.data.forecast_created,
        }

"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    async_add_entities([
        TankMasterLevelSensor(coordinator, config_entry),
        TankMasterVolumeSensor(coordinator, config_entry),
        TankMasterCapacitySensor(coordinator, config_entry),
        TankMasterTemperatureSensor(coordinator, config_entry),
    ])


class TankMasterSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for TankMaster sensors."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_has_entity_name = True
        
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": self._config_entry.data.get("name", "TankMaster"),
            "manufacturer": "TankMaster",
            "model": "Tank Monitor",
        }


class TankMasterLevelSensor(TankMasterSensorBase):
    """Representation of a TankMaster Level Sensor."""

    _attr_name = "Level"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_level"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("level")


class TankMasterVolumeSensor(TankMasterSensorBase):
    """Representation of a TankMaster Volume Sensor."""

    _attr_name = "Volume"
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_device_class = SensorDeviceClass.VOLUME
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_volume"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("volume")


class TankMasterCapacitySensor(TankMasterSensorBase):
    """Representation of a TankMaster Capacity Sensor."""

    _attr_name = "Capacity"
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_device_class = SensorDeviceClass.VOLUME
    _attr_state_class = SensorStateClass.TOTAL

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_capacity"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("capacity")


class TankMasterTemperatureSensor(TankMasterSensorBase):
    """Representation of a TankMaster Temperature Sensor."""

    _attr_name = "Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._config_entry.entry_id}_temperature"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("temperature")

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TankMasterCoordinator

# Default thresholds if not yet configurable
DEFAULT_THRESHOLDS = [25, 50, 75, 90]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    coordinator: TankMasterCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        TankMasterLevelSensor(coordinator, entry),
        TankMasterFirmwareSensor(coordinator, entry),
    ]

    # Create up to 4 probe threshold sensors
    for idx in range(4):
        entities.append(
            TankMasterProbeThresholdSensor(coordinator, entry, idx)
        )

    async_add_entities(entities)


class TankMasterBase(
    CoordinatorEntity[TankMasterCoordinator], SensorEntity
):
    def __init__(
        self,
        coordinator: TankMasterCoordinator,
        entry: ConfigEntry,
    ):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self.coordinator.name,
            manufacturer="RiVöt",
            model="TankMaster",
            sw_version=self.coordinator.data.get("fw"),
        )


class TankMasterLevelSensor(TankMasterBase):
    _attr_name = "Tank Level"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:water-percent"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_level"

    @property
    def native_value(self):
        return self.coordinator.data.get("level")


class TankMasterFirmwareSensor(TankMasterBase):
    _attr_name = "Firmware Version"
    _attr_icon = "mdi:chip"
    _attr_entity_category = "diagnostic"

    @property
    def unique_id(self) -> str:
        return f"{self._entry.entry_id}_firmware"

    @property
    def native_value(self):
        return self.coordinator.data.get("fw")


class TankMasterProbeThresholdSensor(TankMasterBase):
    def __init__(
        self,
        coordinator: TankMasterCoordinator,
        entry: ConfigEntry,
        index: int,
    ):
        super().__init__(coordinator, entry)
        self._index = index

        self._attr_name = f"Probe {index + 1} Threshold"
        self._attr_icon = "mdi:gauge"
        self._attr_entity_category = "diagnostic"

    @property
    def unique_id(self) -> str:
        return (
            f"{self._entry.entry_id}_probe_{self._index}_threshold"
        )

    @property
    def native_value(self):
        thresholds = self.coordinator.data.get(
            "thresholds", DEFAULT_THRESHOLDS
        )
        if self._index < len(thresholds):
            return thresholds[self._index]
        return None

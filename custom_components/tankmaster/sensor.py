from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TankMasterCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: TankMasterCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TankMasterLevelSensor(coordinator, entry),
        TankMasterProbeSensor(coordinator, entry, 0),
        TankMasterProbeSensor(coordinator, entry, 1),
        TankMasterProbeSensor(coordinator, entry, 2),
        TankMasterProbeSensor(coordinator, entry, 3),
        TankMasterFirmwareSensor(coordinator, entry),
    ]
    async_add_entities(entities)


class TankMasterBase(CoordinatorEntity[TankMasterCoordinator]):
    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self.host = coordinator.host

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.host)},
            name=f"TankMaster ({self.host})",
            manufacturer="RiVöt / UGotToad",
            model="TankMaster",
            configuration_url=f"http://{self.host}/",
        )


class TankMasterProbeSensor(TankMasterBase, SensorEntity):
    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry, idx: int) -> None:
        super().__init__(coordinator, entry)
        self.idx = idx
        self._attr_name = f"TankMaster Probe {idx+1}"
        self._attr_unique_id = f"{self.host}_probe_{idx+1}"
        self._attr_native_unit_of_measurement = "%"

    @property
    def native_value(self) -> int | None:
        values = (self.coordinator.data or {}).get("sensorValues")
        if not isinstance(values, list) or len(values) <= self.idx:
            return None
        try:
            return int(values[self.idx])
        except Exception:
            return None


class TankMasterLevelSensor(TankMasterBase, SensorEntity):
    """Computed level = max(probe values)."""

    _attr_name = "TankMaster Level"
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_level_percent"

    @property
    def native_value(self) -> int | None:
        values = (self.coordinator.data or {}).get("sensorValues")
        if not isinstance(values, list) or not values:
            return None
        try:
            nums = [int(v) for v in values if v is not None]
            return max(nums) if nums else None
        except Exception:
            return None


class TankMasterFirmwareSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Firmware"
    _attr_icon = "mdi:chip"

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_firmware"

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("firmwareVersion")

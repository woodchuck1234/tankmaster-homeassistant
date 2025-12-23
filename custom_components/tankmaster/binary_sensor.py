from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import TankMasterCoordinator
from .sensor import TankMasterBase


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: TankMasterCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = [
        TankMasterProbeDetected(coordinator, entry, 0),
        TankMasterProbeDetected(coordinator, entry, 1),
        TankMasterProbeDetected(coordinator, entry, 2),
        TankMasterProbeDetected(coordinator, entry, 3),
        TankMasterWifiConnected(coordinator, entry),
        TankMasterExternalPower(coordinator, entry),
    ]
    async_add_entities(entities)


class TankMasterProbeDetected(TankMasterBase, BinarySensorEntity):
    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry, idx: int) -> None:
        super().__init__(coordinator, entry)
        self.idx = idx
        self._attr_name = f"TankMaster Probe {idx+1} Liquid Detected"
        self._attr_unique_id = f"{self.host}_probe_{idx+1}_detected"
        self._attr_icon = "mdi:water"
        self._attr_entity_registry_enabled_default = False

    @property
    def is_on(self) -> bool | None:
        values = (self.coordinator.data or {}).get("sensorValues")
        if not isinstance(values, list) or len(values) <= self.idx:
            return None
        try:
            raw = int(values[self.idx])  # 0 or 100
            return raw >= 50             # wet if 100
        except Exception:
            return None


class TankMasterWifiConnected(TankMasterBase, BinarySensorEntity):
    _attr_name = "TankMaster Wi-Fi Connected"
    _attr_icon = "mdi:wifi"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_wifi_connected"

    @property
    def is_on(self) -> bool | None:
        v = (self.coordinator.data or {}).get("wifiConnected")
        return bool(v) if v is not None else None


class TankMasterExternalPower(TankMasterBase, BinarySensorEntity):
    _attr_name = "TankMaster External Power"
    _attr_icon = "mdi:power-plug"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_external_power"

    @property
    def is_on(self) -> bool | None:
        v = (self.coordinator.data or {}).get("externalPower")
        return bool(v) if v is not None else None

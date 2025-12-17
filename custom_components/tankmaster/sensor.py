from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TankMasterCoordinator

# Default thresholds if you don't expose them as config options (yet)
DEFAULT_THRESHOLDS = [25, 50, 75, 90]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: TankMasterCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        TankMasterLevelSensor(coordinator, entry),
        TankMasterFirmwareSensor(coordinator, entry),
    ]

    # Create up to 4 probe sensors (you can later make this dynamic via numSensors)
    for idx in range(4):
        entities.append(TankMasterProbeThresholdSensor(coordinator, entry, idx))

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


class TankMasterProbeThresholdSensor(TankMasterBase, SensorEntity):
    """Shows probe threshold percent when wet; 0 when dry."""

    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:water-percent"

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry, idx: int) -> None:
        super().__init__(coordinator, entry)
        self.idx = idx
        threshold = DEFAULT_THRESHOLDS[idx] if idx < len(DEFAULT_THRESHOLDS) else (idx + 1) * 25
        self.threshold = threshold

        self._attr_name = f"TankMaster Probe {idx+1}"
        self._attr_unique_id = f"{self.host}_probe_{idx+1}_threshold"

    @property
    def native_value(self) -> int | None:
        values = (self.coordinator.data or {}).get("sensorValues")
        if not isinstance(values, list) or len(values) <= self.idx:
            return None

        try:
            raw = int(values[self.idx])  # TankMaster returns 0 or 100
        except Exception:
            return None

        return self.threshold if raw >= 50 else 0  # wet -> threshold, dry -> 0

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "threshold_percent": self.threshold,
            "raw_value": (self.coordinator.data or {}).get("sensorValues", [None]*4)[self.idx],
        }


class TankMasterLevelSensor(TankMasterBase, SensorEntity):
    """Computed tank level = highest threshold whose probe is wet."""

    _attr_name = "TankMaster Level"
    _attr_unique_id = None  # set in __init__
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:water"

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_level_percent"

    @property
    def native_value(self) -> int | None:
        values = (self.coordinator.data or {}).get("sensorValues")
        if not isinstance(values, list) or not values:
            return None

        level = 0
        for i, threshold in enumerate(DEFAULT_THRESHOLDS[: len(values)]):
            try:
                raw = int(values[i])
            except Exception:
                continue
            if raw >= 50:  # wet
                level = max(level, threshold)

        return level

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "probe_thresholds": DEFAULT_THRESHOLDS,
            "sensorValues_raw": (self.coordinator.data or {}).get("sensorValues"),
        }


class TankMasterFirmwareSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Firmware"
    _attr_icon = "mdi:chip"

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_firmware"

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("firmwareVersion")

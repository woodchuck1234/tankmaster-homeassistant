from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
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

        # New diagnostics from coordinator.py merge (/api/device + /api/network)
        TankMasterDeviceNameSensor(coordinator, entry),
        TankMasterWifiSsidSensor(coordinator, entry),
        TankMasterWifiRssiSensor(coordinator, entry),
        TankMasterUptimeSensor(coordinator, entry),
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
        data = self.coordinator.data or {}
        device_name = data.get("deviceName") or f"TankMaster ({self.host})"
        return DeviceInfo(
            identifiers={(DOMAIN, self.host)},
            name=str(device_name),
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
        values = (self.coordinator.data or {}).get("sensorValues") or [None] * 4
        raw_val = values[self.idx] if isinstance(values, list) and len(values) > self.idx else None
        return {
            "threshold_percent": self.threshold,
            "raw_value": raw_val,
        }


class TankMasterLevelSensor(TankMasterBase, SensorEntity):
    """Computed tank level = highest threshold whose probe is wet."""

    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:water"

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_name = "TankMaster Level"
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
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_firmware"

    @property
    def native_value(self) -> str | None:
        val = (self.coordinator.data or {}).get("firmwareVersion")
        return str(val) if val is not None else None


class TankMasterDeviceNameSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Device Name"
    _attr_icon = "mdi:tag"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_device_name"

    @property
    def native_value(self) -> str | None:
        val = (self.coordinator.data or {}).get("deviceName")
        return str(val) if val else None


class TankMasterWifiSsidSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Wi-Fi SSID"
    _attr_icon = "mdi:wifi"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_wifi_ssid"

    @property
    def native_value(self) -> str | None:
        val = (self.coordinator.data or {}).get("wifi_ssid")
        return str(val) if val else None


class TankMasterWifiRssiSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Wi-Fi RSSI"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = "dBm"
    _attr_icon = "mdi:wifi"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_wifi_rssi"

    @property
    def native_value(self) -> int | None:
        val = (self.coordinator.data or {}).get("wifi_rssi")
        if val is None:
            return None
        try:
            return int(val)
        except Exception:
            return None


class TankMasterUptimeSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Uptime"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_uptime_seconds"

    @property
    def native_value(self) -> int | None:
        val = (self.coordinator.data or {}).get("uptime_seconds")
        if val is None:
            return None
        try:
            return int(val)
        except Exception:
            return None

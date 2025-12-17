from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .coordinator import TankMasterCoordinator

# Default thresholds (matches your “S1/S2/S3/S4” behavior)
DEFAULT_THRESHOLDS = [25, 50, 75, 90]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: TankMasterCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        TankMasterLevelSensor(coordinator, entry),
        TankMasterFirmwareSensor(coordinator, entry),
        TankMasterDeviceNameSensor(coordinator, entry),
        TankMasterWifiSSIDSensor(coordinator, entry),
        TankMasterWifiRSSISensor(coordinator, entry),
        TankMasterUptimeSensor(coordinator, entry),
    ]

    # Create up to 4 probe sensors
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
        # NOTE: if you want the Device Name from firmware to show up as the HA device name,
        # you'll need to move this into a custom device registry update. For now we keep it stable.
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

        return self.threshold if raw >= 50 else 0

    @property
    def extra_state_attributes(self) -> dict:
        raw_list = (self.coordinator.data or {}).get("sensorValues")
        raw_value = None
        if isinstance(raw_list, list) and len(raw_list) > self.idx:
            raw_value = raw_list[self.idx]

        return {
            "threshold_percent": self.threshold,
            "raw_value": raw_value,
        }


class TankMasterLevelSensor(TankMasterBase, SensorEntity):
    """Computed tank level = highest threshold whose probe is wet."""

    _attr_name = "TankMaster Level"
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
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_firmware"

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("firmwareVersion")


class TankMasterDeviceNameSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Device Name"
    _attr_icon = "mdi:tag"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_device_name"

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("deviceName")


class TankMasterWifiSSIDSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Wi-Fi SSID"
    _attr_icon = "mdi:wifi"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_wifi_ssid"

    @property
    def native_value(self) -> str | None:
        return (self.coordinator.data or {}).get("wifiSSID")


class TankMasterWifiRSSISensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Wi-Fi RSSI"
    _attr_icon = "mdi:wifi-strength-2"
    _attr_native_unit_of_measurement = "dBm"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_wifi_rssi"

    @property
    def native_value(self) -> int | None:
        v = (self.coordinator.data or {}).get("wifiRSSI")
        try:
            return int(v) if v is not None else None
        except Exception:
            return None


class TankMasterUptimeSensor(TankMasterBase, SensorEntity):
    _attr_name = "TankMaster Uptime"
    _attr_icon = "mdi:timer-outline"
    _attr_native_unit_of_measurement = "s"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: TankMasterCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self.host}_uptime"

    @property
    def native_value(self) -> int | None:
        v = (self.coordinator.data or {}).get("uptimeSeconds")
        try:
            return int(v) if v is not None else None
        except Exception:
            return None

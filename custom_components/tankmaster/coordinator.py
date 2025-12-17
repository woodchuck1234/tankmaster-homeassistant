from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, CONF_HOST, DOMAIN


class TankMasterCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _fetch_json(self, path: str) -> dict[str, Any]:
        url = f"http://{self.host}{path}"
        try:
            async with self.session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status} for {path}")
                data = await resp.json()
                if not isinstance(data, dict):
                    raise UpdateFailed(f"Invalid JSON from {path}")
                return data
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout fetching {path}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"HTTP error fetching {path}: {err}") from err

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            status_task = self._fetch_json("/api/status")
            device_task = self._fetch_json("/api/device")
            network_task = self._fetch_json("/api/network")

            status, device, network = await asyncio.gather(
                status_task, device_task, network_task
            )

            data: dict[str, Any] = {}
            data.update(status or {})
            data.update(device or {})

            # Pull wifi.* fields out of /api/network
            wifi = (network or {}).get("wifi") or {}
            data["wifi_ssid"] = wifi.get("ssid") or None
            data["wifi_rssi"] = wifi.get("rssi")  # may be None
            if "connected" in wifi:
                data["wifiConnected"] = bool(wifi.get("connected"))

            # Normalize uptime: /api/device returns millis() (ms)
            uptime_ms = data.get("uptime")
            if isinstance(uptime_ms, (int, float)):
                data["uptime_seconds"] = int(uptime_ms // 1000)
            else:
                data["uptime_seconds"] = None

            return data

        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(str(err)) from err

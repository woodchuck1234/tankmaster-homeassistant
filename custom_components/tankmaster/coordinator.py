from __future__ import annotations

from time import monotonic
import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TankMasterCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.session = async_get_clientsession(hass)

        self._last_diag = 0.0
        self._diag_interval = 900.0  # 15 minutes
        self._last_device: dict = {}
        self._last_network: dict = {}
        self._last_system: dict = {}

        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _fetch_json(self, path: str, timeout_s: float = 20.0) -> dict:
        """Fetch JSON from TankMaster. Raises UpdateFailed on hard errors."""
        url = f"http://{self.host}{path}"
        timeout = aiohttp.ClientTimeout(total=timeout_s)

        async with self.session.get(url, timeout=timeout) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"{path} HTTP {resp.status}")

            data = await resp.json()
            if not isinstance(data, dict):
                raise UpdateFailed(f"{path} invalid JSON")

            return data

    async def _async_update_data(self) -> dict:
        """Fetch /api/status plus optional diagnostic endpoints and merge results."""
        try:
            # Required endpoint (drives your main sensors)
            status = await self._fetch_json("/api/status")

            # Optional endpoints: do not fail the whole integration if these flake out
            async def safe(path: str) -> dict:
                try:
                    return await self._fetch_json(path)
                except Exception as e:
                    _LOGGER.debug("TankMaster optional fetch failed %s: %s", path, e)
                    return {}

            # Decide whether to refresh diagnostics (every 15 minutes)
            now = monotonic()
            if (now - self._last_diag) >= self._diag_interval:
                self._last_diag = now
                # Fetch optional endpoints sequentially to avoid overwhelming ESP32
                device = await safe("/api/device")
                await asyncio.sleep(0.2)
                network = await safe("/api/network")
                await asyncio.sleep(0.2)
                system = await safe("/api/system")
                # Cache successful results (even if some are empty)
                self._last_device = device
                self._last_network = network
                self._last_system = system
            else:
                device = self._last_device
                network = self._last_network
                system = self._last_system

            merged: dict = dict(status)

            # Keep the raw payloads too (handy for debugging / future sensors)
            merged["device"] = device
            merged["network"] = network
            merged["system"] = system

            # Flatten the values we care about into stable keys
            if isinstance(device, dict) and "deviceName" in device:
                merged["deviceName"] = device.get("deviceName")

            wifi = {}
            if isinstance(network, dict):
                wifi = network.get("wifi") or {}
            if isinstance(wifi, dict):
                merged["wifiSSID"] = wifi.get("ssid")
                merged["wifiRSSI"] = wifi.get("rssi")

            # Prefer /api/system uptime (seconds). /api/device uptime is millis() in your firmware snippet.
            if isinstance(system, dict) and "uptime" in system:
                merged["uptimeSeconds"] = system.get("uptime")
            elif isinstance(device, dict) and "uptime" in device:
                try:
                    merged["uptimeSeconds"] = int(device.get("uptime")) // 1000
                except Exception:
                    pass

            return merged

        except Exception as err:
            raise UpdateFailed(str(err)) from err

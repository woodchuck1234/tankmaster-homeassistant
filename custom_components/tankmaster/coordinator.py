from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, CONF_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TankMasterCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.session = async_get_clientsession(hass)

        # track consecutive failures so entities can "grace" a couple misses
        self._consecutive_failures = 0

        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{self.host}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _fetch_status(self) -> dict:
        url = f"http://{self.host}/api/status"
        timeout = aiohttp.ClientTimeout(total=20)

        async with self.session.get(url, timeout=timeout) as resp:
            if resp.status != 200:
                raise UpdateFailed(f"HTTP {resp.status}")
            data = await resp.json()
            if not isinstance(data, dict):
                raise UpdateFailed("Invalid JSON")
            return data

    async def _async_update_data(self) -> dict:
        try:
            data = await self._fetch_status()
            self._consecutive_failures = 0
            return data

        except Exception as err:
            # Optional: one quick retry after a short delay helps on flaky Wi-Fi
            try:
                await asyncio.sleep(0.5)
                data = await self._fetch_status()
                self._consecutive_failures = 0
                return data
            except Exception:
                self._consecutive_failures += 1
                raise UpdateFailed(str(err)) from err

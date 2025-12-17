from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_HOST


async def _can_connect(hass: HomeAssistant, host: str) -> bool:
    session = async_get_clientsession(hass)
    url = f"http://{host}/api/status"
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                return False
            data = await resp.json()
            # minimal sanity check
            return isinstance(data, dict) and "sensorValues" in data
    except Exception:
        return False


class TankMasterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()

            # Unique by host (good enough for v0.1)
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            if await _can_connect(self.hass, host):
                return self.async_create_entry(title=f"TankMaster ({host})", data={CONF_HOST: host})

            errors["base"] = "cannot_connect"

        schema = vol.Schema({vol.Required(CONF_HOST): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

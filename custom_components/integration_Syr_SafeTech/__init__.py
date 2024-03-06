"""The Syr integration"""
from __future__ import annotations
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_IP, DOMAIN
from .SafeTech import SafeTech
from .UpdateCoordinator import UpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup Syr with config entry."""  # noqa: D401
    # _LOGGER.debug("async_setup_entry __init__")
    hass.data.setdefault(DOMAIN, {})
    my_SafeTech = SafeTech(entry.data[CONF_IP])
    SafeTech_data_coordinator = UpdateCoordinator(hass, SafeTech_api=my_SafeTech)

    await SafeTech_data_coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = SafeTech_data_coordinator

    """Register Handler for options flow update."""
    entry.add_update_listener(update_listener)

    await hass.config_entries.async_forward_entry_setups(entry, (Platform.SENSOR,))
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    # for key in entry.options:
    #    _LOGGER.info("%s - %s", key, entry.options[key])

    hass.config_entries.async_update_entry(entry, options=entry.options)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")

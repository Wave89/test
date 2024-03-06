"""Coordinator for SafeTech."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import update_coordinator

from .const import DOMAIN, POLL_INTERVAL
from .SafeTech import SafeTech

_LOGGER = logging.getLogger(__name__)


class UpdateCoordinator(update_coordinator.DataUpdateCoordinator):
    """Class to manage fetching Opengarage data."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        SafeTech_api: SafeTech,
    ) -> None:
        """Initialize global SafeTech data updater."""
        self.SafeTech_api = SafeTech_api

        _LOGGER.info("Load poll interval: %s", POLL_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=POLL_INTERVAL),
        )

    async def _async_update_data(self) -> None:
        """Fetch data."""
        _LOGGER.debug("UpdateCoordinator _async_update_data")
        try:
            await self.SafeTech_api.update_stats()
        except Exception as err:
            raise ConfigEntryNotReady(repr(err)) from err
        return self.SafeTech_api.state

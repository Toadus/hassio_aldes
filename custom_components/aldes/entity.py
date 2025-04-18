import logging
import asyncio
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .aldes.product import AldesProduct
from .const import DOMAIN, INTEGRATION, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class AldesProductDataUpdateCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, product: AldesProduct) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name = f'{DOMAIN}-{product.id}',
            update_interval = SCAN_INTERVAL,
            request_refresh_debouncer = Debouncer(
                hass, _LOGGER, cooldown = 5, immediate = False
            )
        )
        
        self.product = product
        self._mode_change_polling_active = False

    async def _async_update_data(self) -> None:
        await self.product.update()
        
    async def accelerated_refresh_after_mode_change(self) -> None:
        """
        Performs accelerated polling after a mode change:
        - Immediate poll after 1 second
        - Two subsequent polls at 3 second intervals
        - Return to normal polling interval
        """
        # Prevent multiple accelerated polling sequences from running simultaneously
        if self._mode_change_polling_active:
            return
            
        self._mode_change_polling_active = True
        
        try:
            # Store original update interval to restore it later
            original_interval = self.update_interval
            
            # First poll after 1 second
            self.update_interval = timedelta(seconds=1)
            await asyncio.sleep(1)
            await self.async_refresh()
            
            # Two polls at 3-second intervals
            self.update_interval = timedelta(seconds=3)
            for _ in range(2):
                await asyncio.sleep(3)
                await self.async_refresh()
                
            # Restore normal polling interval
            self.update_interval = original_interval
            
        finally:
            self._mode_change_polling_active = False

class AldesProductEntity(CoordinatorEntity[AldesProductDataUpdateCoordinator]):

    def __init__(self, coordinator: AldesProductDataUpdateCoordinator, entity_suffix: str) -> None:
        super().__init__(coordinator)
        
        product = coordinator.product
        self._attr_name = f'{product.get_display_name()} {entity_suffix}'
        self._attr_unique_id = f'{product.id}-{entity_suffix.lower().replace(" ", "-")}'
        self._attr_device_info = DeviceInfo(
            identifiers  = {(DOMAIN, product.id)},
            manufacturer = INTEGRATION,
            model        = product.get_display_name(),
            name         = product.name
        )

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.const import UnitOfTemperature
from typing import Any, Optional

from .const import DOMAIN, PRODUCT_COORDINATORS
from .entity import AldesProductDataUpdateCoordinator, AldesProductEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id][PRODUCT_COORDINATORS]
    
    entities = []
    
    # Create sensors for each coordinator
    for coordinator in coordinators:
        # Get the available sensors for this product
        sensors = coordinator.product.get_available_sensors()
        
        # Create a sensor entity for each defined sensor
        for sensor_id, sensor_config in sensors.items():
            entities.append(
                AldesProductSensor(
                    coordinator=coordinator,
                    sensor_id=sensor_id,
                    name=sensor_config['name'],
                    icon=sensor_config.get('icon'),
                    device_class=sensor_config.get('device_class'),
                    unit_of_measurement=sensor_config.get('unit'),
                    state_class=sensor_config.get('state_class'),
                    entity_category=sensor_config.get('entity_category')
                )
            )
    
    async_add_entities(entities)


class AldesProductSensor(AldesProductEntity, SensorEntity):
    """Representation of an Aldes product sensor."""

    def __init__(self, 
                 coordinator: AldesProductDataUpdateCoordinator,
                 sensor_id: str,
                 name: str,
                 icon: Optional[str] = None,
                 device_class: Optional[str] = None,
                 unit_of_measurement: Optional[str] = None,
                 state_class: Optional[str] = None,
                 entity_category: Optional[str] = None) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, name)
        
        self._sensor_id = sensor_id
        
        if icon:
            self._attr_icon = icon
            
        if device_class:
            if device_class == 'temperature':
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
            elif device_class == 'date':
                self._attr_device_class = SensorDeviceClass.DATE
            elif device_class == 'volume_flow_rate':
                self._attr_device_class = SensorDeviceClass.VOLUME_FLOW_RATE
                
        if unit_of_measurement:
            self._attr_native_unit_of_measurement = unit_of_measurement
            if unit_of_measurement == '°C':
                self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
                
        if state_class:
            self._attr_state_class = state_class
            
        if entity_category == 'diagnostic':
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        elif entity_category == 'config':
            self._attr_entity_category = EntityCategory.CONFIG

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.coordinator.product.get_sensor_value(self._sensor_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

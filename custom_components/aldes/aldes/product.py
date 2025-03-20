from __future__ import annotations

from typing import Final, List, Dict, Any, Optional
from datetime import datetime

# Fix the import statement
from . import api

HOLIDAYS_MODE: Final = 'W'

def is_product_supported(reference: str) -> bool:
    return _DISPLAY_NAMES.get(reference) is not None

_MODES = {
    'Holidays' : HOLIDAYS_MODE,
    'Daily'    : 'V',
    'Boost'    : 'Y',
    'Guest'    : 'X',
    'Air Prog' : 'Z'
}

_DISPLAY_NAMES: Final = {
    'AIR_TOP' : 'InspirAIR TOP'
}

# Sensor definitions
_SENSORS = {
    'last_filter_change': {
        'key': 'dateLastFilterUpdate',
        'name': 'Last Filter Change', 
        'icon': 'mdi:air-filter',
        'device_class': 'date',
        'entity_category': 'diagnostic'
    },
    'current_mode': {
        'key': 'AIR_CURRENT_MODE',
        'name': 'Current Mode',
        'icon': 'mdi:fan',
        'entity_category': 'diagnostic'
    },
    'exit_air_flow': {
        'key': 'AIR_EXTF_FLW',
        'name': 'Exit Air Flow',
        'icon': 'mdi:air-filter',
        'unit': 'm³/h',
        'device_class': 'volume_flow_rate',
        'entity_category': 'diagnostic'
    },
    'exit_air_speed': {
        'key': 'AIR_EXTF_SPD',
        'name': 'Exit Air Motor Speed',
        'icon': 'mdi:fan-speed-1',
        'unit': 'rpm',
        'entity_category': 'diagnostic'
    },
    'exit_air_temperature': {
        'key': 'AIR_EXT_TPT',
        'name': 'Exit Air Temperature',
        'icon': 'mdi:thermometer',
        'unit': '°C',
        'device_class': 'temperature',
        'state_class': 'measurement',
        'entity_category': 'diagnostic'
    },
    'intake_air_flow': {
        'key': 'AIR_FFE_FLW',
        'name': 'Intake Air Flow',
        'icon': 'mdi:air-filter',
        'unit': 'm³/h',
        'device_class': 'volume_flow_rate',
        'entity_category': 'diagnostic'
    },
    'outside_temperature': {
        'key': 'AIR_OUTSIDE_TPT',
        'name': 'Outside Temperature',
        'icon': 'mdi:thermometer',
        'unit': '°C',
        'device_class': 'temperature',
        'state_class': 'measurement',
        'entity_category': 'diagnostic'
    },
    'reject_air_temperature': {
        'key': 'AIR_REJECT_TPT',
        'name': 'Rejected Air Temperature',
        'icon': 'mdi:thermometer',
        'unit': '°C',
        'device_class': 'temperature',
        'state_class': 'measurement',
        'entity_category': 'diagnostic'
    },
    'intake_air_speed': {
        'key': 'AIR_VI_SPD',
        'name': 'Intake Air Motor Speed',
        'icon': 'mdi:fan-speed-1',
        'unit': 'rpm',
        'entity_category': 'diagnostic'
    }
}

class AldesProduct:
    def __init__(self, aldesApi: api.AldesApi, id: str, name: str, mode: str, tmpcu: str):
        self._aldesApi = aldesApi
        self._id       = id
        self._name     = name
        self._mode     = mode
        self._tmpcu    = tmpcu
        self._product_data = {}
    
    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name
    
    def get_display_name(self) -> str:
        return _DISPLAY_NAMES.get(self._name, self._name)
    
    def get_display_modes(self) -> List[str]:
        return list(_MODES.keys())

    def get_display_mode(self) -> str:
        for display_mode, mode in _MODES.items():
            if mode == self._mode:
                return display_mode
        
        raise ValueError(f'Mode {self._mode} is not managed, please report.')
    
    def get_available_sensors(self) -> Dict[str, Dict[str, Any]]:
        return _SENSORS
    
    def get_sensor_value(self, sensor_id: str) -> Optional[Any]:
        if not self._product_data:
            return None
            
        sensor_info = _SENSORS.get(sensor_id)
        if not sensor_info:
            return None
            
        key = sensor_info['key']
        
        # Extract last filter change date directly from the product data
        if key == 'dateLastFilterUpdate' and key in self._product_data:
            try:
                date_str = self._product_data[key]
                # Convert to date object
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%SZ').date()
            except (ValueError, TypeError):
                return None
                
        # For other sensors, look in the indicator data
        if not self._product_data or 'indicator' not in self._product_data:
            return None
            
        indicator = self._product_data['indicator']
        if key in indicator:
            return indicator[key]
            
        return None

    async def maybe_set_mode_from_display(self, display_mode: str) -> None:
        await self._aldesApi.request_set_mode(self._id, _MODES[display_mode])
    
    async def update(self) -> None:
        data = await self._aldesApi.get_product(self._id)
        if (mode := data.get('mode')) is not None:
            self._mode = mode
        if (tmpcu := data.get('tmpcu')) is not None:
            self._tmpcu = tmpcu
        if (product_data := data.get('product_data')) is not None:
            self._product_data = product_data

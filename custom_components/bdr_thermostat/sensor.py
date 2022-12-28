import logging
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from datetime import timedelta
from typing import Callable, Optional
from .const import *
from homeassistant.const import (
    CONF_NAME,
)

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=10)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:

    config = hass.data[PLATFORM].get(DATA_KEY_CONFIG)

    _LOGGER.warning(
        "Setup entity coming from configuration.yaml named: %s. Device will not be created, only entities",
        config.get(CONF_NAME),
    )

    await async_setup_reload_service(hass, "sensor", PLATFORM)
    async_add_entities(
        [
			WaterPressureSensor(hass, config),
            ErrorSensor(hass, config), 
            FlowTemperatureSensor(hass, config),
			OutsideTemperatureSensor(hass, config),
			HeatingSensor(hass, config),
			EnergyConsumptionSensor(hass, config),
            EnergyWaterConsumptionSensor(hass, config),
			TotalEnergyConsumptionSensor(hass, config),
			BurningHoursSensor(hass, config),
            BurningHoursWaterSensor(hass, config)
        ],
        update_before_add=True,
    )


async def async_setup_entry(hass, config_entry, async_add_devices):
    await async_setup_reload_service(hass, DOMAIN, PLATFORM)
    async_add_devices(
        [
            WaterPressureSensor(hass, config_entry.data),
            ErrorSensor(hass, config_entry.data),
            FlowTemperatureSensor(hass, config_entry.data),
			OutsideTemperatureSensor(hass, config_entry.data),
			HeatingSensor(hass, config_entry.data),
			EnergyConsumptionSensor(hass, config_entry.data),
            EnergyWaterConsumptionSensor(hass, config_entry.data),
			TotalEnergyConsumptionSensor(hass, config_entry.data),
			BurningHoursSensor(hass, config_entry.data),
            BurningHoursWaterSensor(hass, config_entry.data)
        ],
        update_before_add=True,
    )     
   
class WaterPressureSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = SensorDeviceClass.PRESSURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Water pressure"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if self._attr_native_unit_of_measurement == "" :
            return False
        else :
            return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        water_pressure = await self._bdr_api.get_water_pressure()

        if water_pressure:
            self._attr_native_value = water_pressure["waterPressure"]["value"]                  
            self._attr_native_unit_of_measurement = water_pressure["waterPressure"]["unit"]
     
        else:
            self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"    



class ErrorSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Errors"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        error = await self._bdr_api.get_errors()

        if error:
            self._attr_native_value = error["status"]                 
            #self._attr_native_unit_of_measurement = outside_temperature["waterPressure"]["unit"]
     
        else:
            #self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"    


class EnergyConsumptionSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Heating consumption"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        consumptions = await self._bdr_api.get_consumptions()
        consumption = consumptions.get("energyCH", None)

        if consumption:
            self._attr_native_value = int(consumption["value"])             
            self._attr_native_unit_of_measurement = consumption["unit"]     

        else:
            self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"   

class EnergyWaterConsumptionSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Water Heating consumption"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        consumptions = await self._bdr_api.get_consumptions()
        consumption = consumptions.get("energyDHW", None)

        if consumption:
            self._attr_native_value = int(consumption["value"])             
            self._attr_native_unit_of_measurement = consumption["unit"]     

        else:
            self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"   

class TotalEnergyConsumptionSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Total Energy consumption"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        consumptions = await self._bdr_api.get_consumptions()
        consumption = consumptions.get("totalEnergy", None)

        if consumption:
            self._attr_native_value = int(consumption["value"])             
            self._attr_native_unit_of_measurement = consumption["unit"]     

        else:
            self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"   

class BurningHoursSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Burning hours"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        consumptions = await self._bdr_api.get_consumptions()
        consumption = consumptions.get("burningHoursCH", None)

        if consumption:
            self._attr_native_value = int(consumption["value"])             
            self._attr_native_unit_of_measurement = consumption["unit"]     

        else:
            self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"   

class BurningHoursWaterSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Burning hours (Water)"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        consumptions = await self._bdr_api.get_consumptions()
        consumption = consumptions.get("burningHoursDHW", None)

        if consumption:
            self._attr_native_value = int(consumption["value"])             
            self._attr_native_unit_of_measurement = consumption["unit"]     

        else:
            self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"  

class FlowTemperatureSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Water temperature"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        water_temperature = await self._bdr_api.get_flow_temperature()

        if water_temperature:
            self._attr_native_value = water_temperature["systemFlowTemperature"]             
            self._attr_native_unit_of_measurement = water_temperature["unit"]
     
        else:
            self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"   

class OutsideTemperatureSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Outside temperature"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        status = await self._bdr_api.get_status()

        if status and status.get("outsideTemperature"):
            self._attr_native_value = status["outsideTemperature"]["value"]          
            self._attr_native_unit_of_measurement = status["outsideTemperature"]["unit"]
     
        else:
            self._attr_native_unit_of_measurement = ""
            self._attr_native_value = "N/A"   

class HeatingSensor(SensorEntity):
    
    def __init__(self, hass, config):
        """Initialize the sensor."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get("serial", "1234"),
                )
            }
		}
        self._attr_name = config.get(CONF_NAME) + " Status"
        self._attr_unique_id = self._attr_name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
    
        status = await self._bdr_api.get_status()

        if status:
            self._attr_native_value = status["zoneActivity"]        
     
        else:
            self._attr_native_value = "N/A"   

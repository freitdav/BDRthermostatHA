import logging
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
)
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from datetime import timedelta
from typing import Any, Callable, Dict, Optional
from .const import *
from .helper import *
from homeassistant.const import (
    CONF_NAME,
    ATTR_TEMPERATURE,
)

from .config_schema import SUPPORT_FLAGS, CLIMATE_SCHEMA
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(CLIMATE_SCHEMA)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:

    config = hass.data[PLATFORM].get(DATA_KEY_CONFIG)

    """Add BdrThermostat entities from configuration.yaml."""
    _LOGGER.warning(
        "Setup entity coming from configuration.yaml named: %s. Device will not be created, only entities",
        config.get(CONF_NAME),
    )
    await async_setup_reload_service(hass, DOMAIN, PLATFORM)

    api = hass.data[PLATFORM].get(DATA_KEY_API)
    async_add_entities(
        # Add new BdrThermostat climate by Zones
        [BdrThermostat(hass, config, zone_name) for zone_name in api.get_zones()],
        update_before_add=True,
    )


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add BdrThermostat entities from user config"""
    await async_setup_reload_service(hass, DOMAIN, PLATFORM)

    api = hass.data[PLATFORM].get(DATA_KEY_API)
    async_add_devices(
        # Add new BdrThermostat climate by Zones
        [
            BdrThermostat(hass, config_entry.data, zone_name)
            for zone_name in api.get_zones()
        ],
        update_before_add=True,
    )


class BdrThermostat(ClimateEntity, RestoreEntity):
    """BdrThermostat"""

    def __init__(self, hass, config, zone_name):
        """Initialize the thermostat."""
        super().__init__()
        self.hass = hass
        self._bdr_api = hass.data[PLATFORM].get(DATA_KEY_API)
        self._attr_name = "BDR - " + zone_name
        self._attr_unique_id = zone_name
        self._attr_supported_features = SUPPORT_FLAGS
        self._attr_preset_modes = PRESET_MODES
        self._attr_hvac_modes = (
            HVAC_MODES
            if self._bdr_api.is_feature_enabled(FEATURE_OPERATING_MODE)
            else [HVAC_MODE_AUTO]
        )
        self._attr_hvac_mode = HVAC_MODE_AUTO
        self._attr_extra_state_attributes = {}
        self._attr_should_poll = True
        self._attr_device_info = {
            "identifiers": {
                (
                    SERIAL_KEY,
                    self._bdr_api.get_device_information().get(SERIAL_KEY, "1234"),
                )
            }
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._bdr_api.is_bootstraped()

    async def async_update(self):
        status = await self._bdr_api.get_status(self._attr_unique_id)
        _LOGGER.debug("Updating BDR status %s", status)

        if status:
            self._attr_current_temperature = status["roomTemperature"]["value"]
            self._attr_temperature_unit = status["roomTemperature"]["unit"]
            self._attr_target_temperature = status.get("roomTemperatureSetpoint").get(
                "value"
            )
            self._attr_preset_mode = preset_mode_bdr_to_ha(
                status["mode"], status["timeProgram"]
            )
            next_switch = status.get("nextSwitch", None)
            if next_switch:
                # Try/Exception because the API is not always returning next_temp values
                try:
                    self._attr_extra_state_attributes["next_change"] = next_switch[
                        "time"
                    ]
                    self._attr_extra_state_attributes["next_temp"] = next_switch[
                        "roomTemperatureSetpoint"
                    ]["value"]
                    self.next_switch_days = next_switch[
                        "dayOffset"
                    ]  # we just need to store this
                except Exception:
                    pass
            else:
                self._attr_extra_state_attributes.pop("next_change", None)
                self._attr_extra_state_attributes.pop("next_temp", None)

        if self._bdr_api.is_feature_enabled(FEATURE_OPERATING_MODE):
            operating_mode = await self._bdr_api.get_operating_mode()

            if operating_mode:
                self._attr_hvac_mode = hvac_mode_bdr_to_ha(operating_mode["mode"])

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        next_change = self._attr_extra_state_attributes.get("next_change", None)

        if next_change:
            # We are in scheduled mode, need to create a temporary override
            override_date = create_override_date(next_change, self.next_switch_days)
            await self._bdr_api.set_override_temperature(
                temperature, override_date, self._attr_unique_id
            )
        else:
            # Manual mode, it is fine to modify the temp
            await self._bdr_api.set_target_temperature(
                temperature, self._attr_unique_id
            )
        await self.async_update_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        target_bdr_mode = hvac_mode_ha_to_bdr(hvac_mode)
        await self._bdr_api.set_operating_mode(target_bdr_mode)
        await self.async_update_ha_state()

    async def async_set_preset_mode(self, preset_mode):
        _LOGGER.debug("Preset mode being set: %s", preset_mode)
        bdr_preset_mode, program = preset_mode_ha_to_bdr(preset_mode)

        self._attr_preset_mode = preset_mode

        # Set a schedule
        if bdr_preset_mode == BDR_PRESET_SCHEDULE:
            await self._bdr_api.set_schedule(program, self._attr_unique_id)
        # Set a manual temperature
        elif bdr_preset_mode == BDR_PRESET_MANUAL:
            await self._bdr_api.set_target_temperature(
                self._attr_target_temperature, self._attr_unique_id
            )
        elif bdr_preset_mode == BDR_PRESET_MODE:
            await self._bdr_api.set_operating_mode(mode=program)

        await self.async_update_ha_state()

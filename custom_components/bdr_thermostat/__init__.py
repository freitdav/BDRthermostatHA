"""The BDR Thermostat integration."""

from .BdrAPI import BdrAPI
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import *
from homeassistant.const import CONF_NAME, CONF_USERNAME, CONF_PASSWORD, Platform
from .config_schema import CONF_PAIR_CODE, CONF_BRAND
from homeassistant.helpers import device_registry as dr

PLATFORMS = [
    Platform.CLIMATE,
    Platform.SENSOR,
]


async def async_setup(hass: HomeAssistant, config) -> bool:
    domain_configs = config.get(DOMAIN, [])
    for domain_config in domain_configs:
        if domain_config.get("platform", False) == PLATFORM:
            api = BdrAPI(
                hass,
                domain_config.get(CONF_USERNAME),
                domain_config.get(CONF_PASSWORD),
                domain_config.get(CONF_PAIR_CODE),
                domain_config.get(CONF_BRAND)
            )
            await api.bootstrap()
            hass.data[PLATFORM] = {DATA_KEY_API: api, DATA_KEY_CONFIG: domain_config}
            if api.is_feature_enabled(FEATURE_ENERGY_CONSUMPTION):
                await hass.helpers.discovery.async_load_platform(
                    Platform.SENSOR, PLATFORM, {}, config
                )
            await hass.helpers.discovery.async_load_platform(
                Platform.CLIMATE, PLATFORM, {}, config
            )
            return True
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(PLATFORM, None)

    return unload_ok


async def async_setup_entry(hass, config_entry):

    api = BdrAPI(
        hass,
        config_entry.data.get(CONF_USERNAME),
        config_entry.data.get(CONF_PASSWORD),
        config_entry.data.get(CONF_PAIR_CODE),
        config_entry.data.get(CONF_BRAND),
    )
    await api.bootstrap()
    hass.data[PLATFORM] = {DATA_KEY_API: api, DATA_KEY_CONFIG: config_entry.data}
    register_device(hass, config_entry, api.get_device_information())
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def update_listener(hass, config_entry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


def register_device(hass, config_entry, device_info):
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(SERIAL_KEY, device_info.get(SERIAL_KEY, "1234"))},
        manufacturer=DEVICE_MANUFACTER,
        name=config_entry.data.get(CONF_NAME),
        model=device_info.get("name", DEVICE_MODEL),
        sw_version=device_info.get("softwareVersion", DEFAULT_VERSION)
    )

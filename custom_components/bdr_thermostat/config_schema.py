import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.climate.const import (
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_PRESET_MODE,
)
from homeassistant.const import CONF_NAME, CONF_USERNAME, CONF_PASSWORD
from .const import (
    DEFAULT_NAME,
)

CONF_PAIR_CODE = "pairing_code"
CONF_BRAND = "brand"


SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE
CLIMATE_SCHEMA = {
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_PAIR_CODE): cv.string,
    vol.Required(
        CONF_BRAND,
        default="baxi",
    ): vol.In(["baxi", "remeha"])}

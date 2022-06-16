from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from .const import DOMAIN
import uuid
import logging
from .config_schema import CLIMATE_SCHEMA
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register("bdr_thermostat")
class BdrThermostatFlowHandler(config_entries.ConfigFlow, domain="bdr_thermostat"):
    """Handle a config flow."""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self._data = {}
        self._unique_id = str(uuid.uuid4())

    async def async_step_import(self, data=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    async def async_step_user(self, user_input=None):
        self._errors = {}
        _LOGGER.debug("user_input= %s", user_input)
        if user_input:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME), data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(CLIMATE_SCHEMA),
            errors=self._errors,
        )

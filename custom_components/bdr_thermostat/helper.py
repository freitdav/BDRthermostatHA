from homeassistant.config_entries import ConfigEntry

from .const import (
    PLATFORM,
    PRESET_MODE_HOLIDAY,
    PRESET_MODE_MANUAL,
    PRESET_MODE_SCHEDULE_1,
    PRESET_MODE_SCHEDULE_2,
    PRESET_MODE_SCHEDULE_3,
    PRESET_MODE_TEMP_OVERRIDE,
    PRESET_MODE_ANTIFROST,
    BDR_PRESET_MANUAL,
    BDR_PRESET_SCHEDULE,
    BDR_PRESET_MODE,
)
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
)
import datetime
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)


def preset_mode_bdr_to_ha(bdr_mode, program=None):

    if bdr_mode == "manual":
        return PRESET_MODE_MANUAL
    elif bdr_mode == "temporary-override":
        return PRESET_MODE_TEMP_OVERRIDE
    elif bdr_mode == "anti-frost":
        return PRESET_MODE_ANTIFROST
    elif bdr_mode == "schedule" and program == 1:
        return PRESET_MODE_SCHEDULE_1
    elif bdr_mode == "schedule" and program == 2:
        return PRESET_MODE_SCHEDULE_2
    elif bdr_mode == "schedule" and program == 3:
        return PRESET_MODE_SCHEDULE_3
    elif bdr_mode == "holiday":
        return PRESET_MODE_HOLIDAY


def preset_mode_ha_to_bdr(ha_mode):

    _LOGGER.info(f"{ha_mode=}")

    if ha_mode == PRESET_MODE_SCHEDULE_1:
        return BDR_PRESET_SCHEDULE, "1"
    elif ha_mode == PRESET_MODE_SCHEDULE_2:
        return BDR_PRESET_SCHEDULE, "2"
    elif ha_mode == PRESET_MODE_SCHEDULE_3:
        return BDR_PRESET_SCHEDULE, "3"
    elif ha_mode == PRESET_MODE_HOLIDAY:
        return BDR_PRESET_MODE, "holiday",
    elif ha_mode == PRESET_MODE_ANTIFROST:
        return BDR_PRESET_MODE, "anti-frost",

    return BDR_PRESET_MANUAL, "manual"

def hvac_mode_bdr_to_ha(raw_mode):
    if raw_mode == "off":
        return HVAC_MODE_OFF
    elif raw_mode == "heating-auto":
        return HVAC_MODE_AUTO


def hvac_mode_ha_to_bdr(ha_mode):
    if ha_mode == HVAC_MODE_AUTO:
        return "heating-auto"
    elif ha_mode == HVAC_MODE_OFF:
        return "off"


def create_override_date(target_time, days_offset):
    now = datetime.datetime.now()
    override_date = now + timedelta(days=days_offset)
    target_hour = int(target_time.split(":")[0])
    target_minutes = int(target_time.split(":")[1])
    override_date = override_date.replace(
        hour=target_hour, minute=target_minutes, second=0, microsecond=0
    )
    return override_date.isoformat("T", "minutes")

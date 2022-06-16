# BDRthermostatHA
BDR (Baxi, De Dietrich, Remeha) thermostat custom integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This component provides custom integration with BDR Thermea branded thermostats. It was tested with Smart TC app and De Dietrich devices.

## How to install
You can use HACS to install this integration as custom repository

If you are not using HACS, you must copy `bdr_thermostat` into your `custom_components` folder on HA

## Configuration
Configuration via integration is recommended. Add an instance of `BDR Thermostat` using the UI:

![](https://github.com/freitdav/BDRthermostatHA/blob/main/pictures/integration.PNG?raw=true)

And follow the steps:

![](https://github.com/freitdav/BDRthermostatHA/blob/main/pictures/setup.PNG?raw=true)


Pairing code can be get from the thermostat device or from the Smart TC app.

## Screenshot
Integration will create a climate entity and several sensor entities. It will look like this in Lovelace dashboard:
![](https://github.com/freitdav/BDRthermostatHA/blob/main/pictures/dashboard.PNG?raw=true)

I used following YAML code:
```yaml
square: false
columns: 1
type: grid
cards:
  - cards:
      - entity: climate.bdr_thermostat
        type: thermostat
        name: Termostat
      - type: entities
        entities:
          - entity: sensor.bdr_thermostat_outside_temperature
            name: Venkovní teplota
          - entity: sensor.bdr_thermostat_status
            name: Stav
          - entity: sensor.bdr_thermostat_water_pressure
            name: Tlak vody
          - entity: sensor.bdr_thermostat_water_temperature
            name: Teplota vody
          - entity: sensor.bdr_thermostat_errors
            name: Chyby
        state_color: true
    type: vertical-stack
```

## Disclaimer
- The code is buggy and integration needs to be reloaded regularly
- Consider doing changes that suite your needs
- Use at your own risk

## Thanks to
- [Domaray](https://community.home-assistant.io/u/Domaray) and [ibernat](https://community.home-assistant.io/u/ibernat) for providing most of the API calls
- [vipial1](https://raw.githubusercontent.com/vipial1/) credits for the core code

# BDRthermostatHA
BDR (Baxi, De Dietrich, Remeha) thermostat custom integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This component provides custom integration with BDR Thermea branded thermostats. It was tested with Smart TC app and De Dietrich devices.

## How to install
You can use HACS to install this integration as custom repository

If you are not using HACS, you must copy `bdr_thermostat` into your `custom_components` folder on HA

## Configuration
Configuration via integration is recommended. Add an instance of `BDR Thermostat` using the UI:
![](https://github.com/vipial1/BAXI_thermostat/blob/main/images/integration.png?raw=true)

And follow the steps:
![](https://github.com/vipial1/BAXI_thermostat/blob/main/images/configuration.png?raw=true)


Is it also possible to configure manually, but then, only entities will be created (not device).
```yaml
climate:
  - platform: bdr_thermostat
    name: My BDR Thermostat
    username: <your username>
    password: <your password>
    pairing_code: <your paring code>
```
Pairing code can be get from the thermostat device or from the Smart TC app, under:
```Settings > Connected devices and services > Invite someone```

## Screenshot
Integration will create a climate entity, that will look like this in Lovelace:
![](https://github.com/vipial1/BAXI_thermostat/blob/main/images/climate.png?raw=true)


## Disclaimer
- The code is buggy and integration needs to be reloaded regularly
- Consider doing changes that suite your needs
- Use at your own risk

## Thanks to
- [Domaray](https://community.home-assistant.io/u/Domaray) and [ibernat](https://community.home-assistant.io/u/ibernat) for providing most of the API calls
- [vipial1](https://raw.githubusercontent.com/vipial1/) credits for the core code

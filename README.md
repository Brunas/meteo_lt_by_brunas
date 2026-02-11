# Meteo.LT by Brunas integration for Home Assistant
<img width="90" height="90" src="https://github.com/Brunas/meteo_lt_by_brunas/blob/main/images/icon.png?raw=true" style="float: left; margin-right: 20px; margin-top: 10px;" >

Home Assistant integration for Meteo.Lt REST API

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<a href="https://buymeacoffee.com/pdfdc52z8h" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="20%"></a>

**IMPORTANT NOTE:** I had to rename integration since there will be/is official meteo.lt integration in Home Assistant core. Unfortunately, that means entities will be renamed too.

This integration adds support for retrieving the Forecast and Hydro data from [Api.Meteo.Lt](https://api.meteo.lt) and setting up following platforms in Home Assistant:

| Platform        | Entity ID                                             | Description                                                                                                                                                                                                                                                                                    |
| --------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `weather`       | `weather.meteo_lt_by_brunas_ABCD`                     | A Home Assistant `weather` entity, with current data, hourly forecast data, and daily forecast data. The first forecast record is treated as current data. Daily forecasts aggregate hourly data per day, using noon conditions for representative weather state.                              |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_current_conditions`   | Sensor with all available weather data taken from the forecast first record and native value set to `temperature`                                                                                                                                                                              |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_temperature`          | Temperature sensor in °C                                                                                                                                                                                                                                                                       |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_apparent_temperature` | Apparent (feels like) temperature sensor in °C                                                                                                                                                                                                                                                 |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_wind_speed`           | Wind speed sensor in m/s                                                                                                                                                                                                                                                                       |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_wind_gust_speed`      | Wind gust speed sensor in m/s                                                                                                                                                                                                                                                                  |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_wind_bearing`         | Wind direction sensor in degrees                                                                                                                                                                                                                                                               |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_cloud_coverage`       | Cloud coverage sensor in %                                                                                                                                                                                                                                                                     |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_pressure`             | Atmospheric pressure sensor in hPa                                                                                                                                                                                                                                                             |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_humidity`             | Humidity sensor in %                                                                                                                                                                                                                                                                           |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_precipitation`        | Precipitation sensor in mm                                                                                                                                                                                                                                                                     |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_condition`            | Weather condition sensor (textual description)                                                                                                                                                                                                                                                 |
| `sensor`        | `sensor.meteo_lt_by_brunas_ABCD_warnings`             | Weather warnings sensor showing count of active warnings. Full detailed information including headline, administrative division, type, severity, description, instruction, and time range is available in extra state attributes of the sensor                                                 |
| `binary_sensor` | `binary_sensor.meteo_lt_by_brunas_ABCD_alerts`        | Binary sensor that indicates if there are any active weather alerts. State is `on` when alerts exist, `off` otherwise. Detailed alert information including headline, administrative division, type, severity, description, instruction, start/end time is available in extra state attributes |
| `sensor`        | `sensor.meteo_lt_by_brunas_EFGH_water_level`          | Water level sensor in cm from nearest hydro station. Historical observations for the past 24 hours are available in extra state attributes of the sensor                                                                                                                                       |
| `sensor`        | `sensor.meteo_lt_by_brunas_EFGH_water_temperature`    | Water temperature sensor in °C from nearest hydro station. Historical observations for the past 24 hours are available in extra state attributes of the sensor                                                                                                                                 |

Where:
- `ABCD` is name of the nearest weather place calculated using place list downloaded from `api.meteo.lt`
- `EFGH` is name of the nearest hydro station calculated using hydro station list downloaded from `api.meteo.lt`

Implementation has been done using Home Assistant version **2025.1.4**. Older versions could work too as long as the new Weather entity forecast types exist. Integration does **not** create Forecast Attributes.

>**NOTE:** At the moment of writing this - api.meteo.lt data renewal happens every 3 hours.

## Translations

The integration supports multiple languages:
- **English** (en) - Default
- **Lithuanian** (lt)

Translations are applied to:
- **Config flow UI**: Integration setup and reconfiguration dialogs
- **Weather warnings**: Headlines, descriptions, and instructions are automatically localized based on your Home Assistant language setting

To use Lithuanian translations, set your Home Assistant language to Lithuanian in **Settings** → **System** → **General** → **Language**.

## Installation through HACS (Recommended Method)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Brunas&repository=meteo_lt_by_brunas&category=integration)

or

1. Go to HACS->Integrations
2. Add this repo into your HACS custom repositories
3. Search for `Meteo.Lt by Brunas Integration` and Download it
4. Restart your HomeAssistant
5. Go to Settings->Devices & Services
6. Shift reload your browser

### Setup the Integration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=meteo_lt_by_brunas)

1. Click Add Integration
1. Search for `Meteo.Lt by Brunas`
1. Select a location using the interactive map or enter latitude and longitude coordinates. Default location is your Home Assistant home location.
1. Unlimitted number of locations is supported. If an entity for the same place exists, new entity gets numeric suffix to the name.
1. You're all set

## Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `meteo_lt_by_brunas`.
1. Download _all_ the files from the `custom_components/meteo_lt_by_brunas/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Add `meteo_lt_by_brunas:` into your `configuration.yaml`
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for `Meteo.Lt by Brunas`:
     - Select a location using the interactive map or enter latitude and longitude coordinates. Default location is your Home Assistant home location.
     - Unlimitted number of locations is supported. If an entity for the same place exists, new entity gets numeric suffix to the name.

## Enable Debug Logging

If logs are needed for debugging or reporting an issue, turn debugging in integration UI or use the following configuration.yaml:

```yaml
logger:
  default: error
  logs:
    custom_components.meteo_lt_by_brunas: debug
```

## Using the Alerts Binary Sensor with Markdown Card

The alerts binary sensor can be used to display weather warnings on your dashboard. Here's an example using the Markdown card:

### Simple Alert Display

```yaml
type: markdown
content: |
  {% if is_state('binary_sensor.meteo_lt_by_brunas_vilnius_alerts', 'on') %}
  ## Weather Alerts Active

  **{{ state_attr('binary_sensor.meteo_lt_by_brunas_vilnius_alerts', 'count') }}** active alert(s)

  {% for alert in state_attr('binary_sensor.meteo_lt_by_brunas_vilnius_alerts', 'alerts') %}
  ---
  **{{ alert.headline }}**
  **Type:** {{ alert.type | title }}
  **Severity:** {{ alert.severity | title }}
  **Administrative division:** {{ alert.administrative_division }}
  **Description:** {{ alert.description }}
  **Recommendations:** {{ alert.instruction }}
  **Start:** {{ alert.start }}
  **End:** {{ alert.end }}
  {% endfor %}
  {% else %}
  ## No Active Weather Alerts
  {% endif %}
title: Weather Alerts
```

### Compact Alert Display

```yaml
type: markdown
content: |
  {% if is_state('binary_sensor.meteo_lt_by_brunas_vilnius_alerts', 'on') %}
  **Weather Alerts:** {{ state_attr('binary_sensor.meteo_lt_by_brunas_vilnius_alerts', 'count') }}
  {% for alert in state_attr('binary_sensor.meteo_lt_by_brunas_vilnius_alerts', 'alerts') %}
  - **{{ alert.headline }}** ({{ alert.severity }}) - {{ alert.administrative_division }}
  {% endfor %}
  {% else %}
  No active alerts
  {% endif %}
```

### Conditional Alert Card (Only Shows When Alerts Exist)

```yaml
type: conditional
conditions:
  - condition: state
    entity: binary_sensor.meteo_lt_by_brunas_vilnius_alerts
    state: 'on'
card:
  type: markdown
  content: |
    # Weather Alert!

    {% for alert in state_attr('binary_sensor.meteo_lt_by_brunas_vilnius_alerts', 'alerts') %}
    **{{ alert.severity | upper }}**: {{ alert.headline }}

    {{ alert.description }}
    {{ alert.instruction }}

    *Valid from {{ alert.start }} to {{ alert.end }}*

    ---
    {% endfor %}
  title: Active Weather Warnings
```

## Alerts Binary Sensor with Button Card

If you prefer a more styled look, you can use `custom:button-card` to render alert blocks with severity-aware colors, camel case alert types, and a compact footer showing forecast and update times.

```yaml
type: conditional
conditions:
  - entity: binary_sensor.meteo_lt_by_brunas_vilnius_alerts
    state: "on"
card:
  type: custom:button-card
  entity: binary_sensor.meteo_lt_by_brunas_vilnius_alerts
  name: >
    [[[ return entity.attributes.friendly_name || 'Alerts'; ]]]
  show_icon: true
  show_name: true
  icon: mdi:alert
  icon_color: >
    [[[
      const alerts = entity.attributes.alerts || [];
      const isRed = alerts.some(a => {
        const sev = (a.severity || '').toLowerCase();
        return sev.includes('stichinis') || sev.includes('red');
      });
      return isRed ? 'red' : 'orange';
    ]]]
  custom_fields:
    alerts: >
      [[[
        const toCamel = (s) => (s || '')
          .toLowerCase()
          .split(/[\s_]+/)
          .filter(Boolean)
          .map(w => w.charAt(0).toUpperCase() + w.slice(1))
          .join(' ');

        const pad = (n) => String(n).padStart(2, '0');
        const fmt = (d) => {
          const dt = new Date(d);
          return `${dt.getFullYear()}-${pad(dt.getMonth()+1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
        };

        const alerts = entity.attributes.alerts || [];
        if (!alerts.length) return 'Refreshing weather data...';

        const seen = new Set();
        const uniq = alerts.filter(a => {
          if (seen.has(a.type)) return false;
          seen.add(a.type);
          return true;
        });

        const blocks = uniq.map(a => {
          const sev = (a.severity || '').toLowerCase();
          const isRed = sev.includes('stichinis') || sev.includes('red');
          const color = isRed ? '#d32f2f' : '#ff9800';
          const bg = isRed ? 'rgba(211,47,47,0.08)' : 'rgba(255,152,0,0.08)';
          const title = toCamel(a.headline);

          return `
            <div style="border-left:4px solid ${color}; background:${bg}; padding:8px; margin:6px 0; border-radius:6px; text-align:left;">
              <div style="font-weight:700; color:${color}; text-align:left;">${title}</div>
              <div style="text-align:left;">${a.description || ''}</div>
              <div style="opacity:0.9; text-align:left;">${a.instruction || ''}</div>
              <div style="font-size:0.85em; opacity:0.75; text-align:left;">
                Expected: ${fmt(a.start)} -> ${fmt(a.end)}
              </div>
            </div>
          `;
        }).join('');

        const footer = `
          <div style="font-size:0.85em; opacity:0.7; margin-top:8px; text-align:left;">
            Forecasted: ${fmt(entity.attributes.forecast_created)} • Updated: ${fmt(entity.attributes.last_updated)}
          </div>
        `;

        return blocks + footer;
      ]]]
  styles:
    card:
      - padding: 12px
      - text-align: left
    grid:
      - justify-items: start
    name:
      - text-align: left
    custom_fields:
      alerts:
        - text-align: left
        - white-space: normal
```

>**Note:** Replace `vilnius` with your actual location name in the entity IDs above.

## Inspired by

[Meteo.lt](https://www.home-assistant.io/integrations/meteo_lt/)

[WeatherFlow Cloud](https://www.home-assistant.io/integrations/weatherflow_cloud/)

[SMHI](https://www.home-assistant.io/integrations/smhi/)

[OpenWeatherMap](https://www.home-assistant.io/integrations/openweathermap/)

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/Brunas/meteo_lt.svg?style=flat-square
[commits]: https://github.com/Brunas/meteo_lt_by_brunas/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square
[license-shield]: https://img.shields.io/github/license/Brunas/meteo_lt_by_brunas.svg?style=flat-square
[maintenance-shield]: https://img.shields.io/badge/maintainer-Brunas%20%40Brunas-blue.svg?style=flat-square
[releases-shield]: https://img.shields.io/github/release/Brunas/meteo_lt_by_brunas.svg?style=flat-square
[releases]: https://github.com/Brunas/meteo_lt_by_brunas/releases

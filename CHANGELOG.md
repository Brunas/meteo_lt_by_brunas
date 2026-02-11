## Release 0.5.2

Date: `2026-02-11`

### Changes

- Added `headline` field to weather warnings in both sensors and binary sensor attributes
- Weather warning properties (`headline`, `description`, `instruction`) are now automatically localized based on Home Assistant language setting (supports English and Lithuanian)
- Enhanced config flow with interactive map-based location selector

## Release 0.5.1

Date: `2026-02-09`

### Changes

- Added `async_forecast_daily` method to calculate daily forecast using a bit optimized hass/meteo.lt integration approach.

## Release 0.5.0

Date: `2026-02-07`

- Upped `meteo_lt-pkg` version to support hydro observations for nearest hydro station and hydro warnings in the same warnings list. Warning instruction has been made a separate property in a warning.
- Warning county renamed to administrative_division since hydro warnings are for municipalities not counties.
- Hydro information added as `water_level` and `water_temperature` sensors with 24 hour historical measurements.
- Changed warnings sensor to present count of warnings when all the details are in attributes part.
- Added binary sensor for alerts based on availability of future weather or hydro warnings. The list of upcoming warnings is in sensor extra attributes. This allows using any specific cards, e.g. markdown, to show flexibly customized alert with details

## Release 0.4.0

Date: `2025-10-20`

### Changes

- Upped `meteo_lt-pkg` version to support weather warnings which will require more work to make them nicely available in Home Assistant
- Upped `homeassistant` package version to `2025.1.4`
- Renamed integration to `meteo_lt_by_brunas` and the name to `Meteo.Lt by Brunas` to avoid confusion with `core/meteo_lt` by LHMT

## Release 0.3.1

Date: `2025-09-30`

### Changes

- HA helper function `sun.is_up` used to identify day

## Release 0.3.0

Date: `2025-09-29`

### Changes

- Introduction condition map from meteo.lt API to HASS (moved from `meteo_lt-pkg`)
- Fixed night time clear sky condition using `sun.sun` state value `above_horizon`
- Usual version bumps

## Release 0.2.6

Date: `2025-05-10`

### Changes

- `Forecast` object usage
- `async_added_to_hass` callback for sensors/weather entity
- Readme and changelog document update
- Usual version bumps

## Release 0.2.5

Date: `2025-03-08`

### Changes

- Country in `hacs.json`
- Usual version bumps

## Release 0.2.4

Date: `2025-01-14`

### Changes

- Daily `dependabot`
- `meteo_lt-pkg` specific version in `requirements.txt`
- Usual version bumps

## Release 0.2.3

Date: `2024-07-31`

### Changes

- Dependabot bumps
- Tweaked sensor device and state classes and units of measurement

## Release 0.2.2

Date: `2024-07-28`

### Changes

- Bumped meteo_lt-pkg to 0.2.2
- Removing of past hours forecasts
- Current conditions is the current hour record
- Forecast creation time stamp in attributes

## Release 0.2.1

Date: `2024-07-28`

### Changes

- Bumped meteo_lt-pkg to 0.2.1 to change UTC datetime format from "Z" to "+00:00"
- Devcontainer fixes and improvements
- Readme update

## Release 0.2.0

Date: `2024-07-27`

### Changes

- Separate sensors for every current conditions attribute
- Added last_updated to all entities to see coordinator working
- Trying to fix updating

## Release 0.1.8

Date: `2024-07-26`

### Changes

- Bumped meteo_lt-pkg to 0.2.0

## Release 0.1.7

Date: `2024-07-25`

### Changes

- Bumped meteo_lt-pkg to 0.1.6

## Release 0.1.6

Date: `2024-07-25`

### Changes

- Readme tweaking

## Not a Release 0.1.x

Date: `2024-07-24`

### Changes

- Initial version moved from local HASS
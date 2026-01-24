"""const.py"""

import logging

DOMAIN = "meteo_lt_by_brunas"
MANUFACTURER = "Meteo.Lt by Brunas"
UPDATE_MINUTES = 30
HYDRO_UPDATE_MINUTES = 60
LOGGER = logging.getLogger(__package__)

# Config keys
CONF_HYDRO_STATION_CODE = "hydro_station_code"
CONF_HYDRO_ENABLE = "enable_hydro"

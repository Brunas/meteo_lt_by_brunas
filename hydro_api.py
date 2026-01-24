"""Hydro API extension for meteo_lt package.

This module extends the meteo_lt API client with hydrological station methods.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class HydroStation:
    """Hydrological station data."""

    code: str
    name: str
    water_body: str
    coordinates: Dict[str, float]  # {"latitude": float, "longitude": float}


@dataclass
class HydroObservation:
    """Single hydrological observation."""

    observation_time_utc: Optional[str] = None
    observation_date_utc: Optional[str] = None
    water_level: Optional[float] = None  # cm
    water_temperature: Optional[float] = None  # °C
    water_discharge: Optional[float] = None  # m3/s


@dataclass
class HydroStationData:
    """Station data with observations."""

    station: HydroStation
    observation_types: List[Dict[str, str]]  # [{"type": "measured|historical", "description": str}]


@dataclass
class HydroObservationData:
    """Observation data response."""

    station: HydroStation
    observations_data_range: Optional[Dict[str, str]] = None
    observations: Optional[List[HydroObservation]] = None


class HydroLtAPI:
    """Extension class for hydrological station API calls."""

    BASE_URL = "https://api.meteo.lt/v1"

    def __init__(self, session=None):
        """Initialize with optional aiohttp session.

        Args:
            session: Optional aiohttp ClientSession. If None, requests won't work.
        """
        self.session = session

    async def get_hydro_stations(self) -> List[HydroStation]:
        """Get list of all hydrological stations.

        Returns:
            List of HydroStation objects.
        """
        if not self.session:
            raise Exception("Session not initialized")

        try:
            async with self.session.get(f"{self.BASE_URL}/hydro-stations") as resp:
                if resp.status == 200:
                    response = await resp.json()
                    stations = []
                    for station_data in response:
                        stations.append(
                            HydroStation(
                                code=station_data.get("code"),
                                name=station_data.get("name"),
                                water_body=station_data.get("waterBody"),
                                coordinates=station_data.get("coordinates", {}),
                            )
                        )
                    return stations
                else:
                    raise Exception(f"API returned status {resp.status}")
        except Exception as e:
            raise Exception(f"Failed to fetch hydrological stations: {e}") from e

    async def get_hydro_station(self, station_code: str) -> HydroStation:
        """Get information about a specific hydrological station.

        Args:
            station_code: The code of the station.

        Returns:
            HydroStation object.
        """
        if not self.session:
            raise Exception("Session not initialized")

        try:
            async with self.session.get(f"{self.BASE_URL}/hydro-stations/{station_code}") as resp:
                if resp.status == 200:
                    response = await resp.json()
                    return HydroStation(
                        code=response.get("code"),
                        name=response.get("name"),
                        water_body=response.get("waterBody"),
                        coordinates=response.get("coordinates", {}),
                    )
                else:
                    raise Exception(f"API returned status {resp.status}")
        except Exception as e:
            raise Exception(f"Failed to fetch hydrological station {station_code}: {e}") from e

    async def get_hydro_observations(
        self, station_code: str
    ) -> HydroStationData:
        """Get available observation types for a station.

        Args:
            station_code: The code of the station.

        Returns:
            HydroStationData with available observation types.
        """
        if not self.session:
            raise Exception("Session not initialized")

        try:
            async with self.session.get(f"{self.BASE_URL}/hydro-stations/{station_code}/observations") as resp:
                if resp.status == 200:
                    response = await resp.json()
                    station = HydroStation(
                        code=response["station"].get("code"),
                        name=response["station"].get("name"),
                        water_body=response["station"].get("waterBody"),
                        coordinates=response["station"].get("coordinates", {}),
                    )
                    observation_types = response.get("observationTypes", [])
                    return HydroStationData(
                        station=station,
                        observation_types=observation_types,
                    )
                else:
                    raise Exception(f"API returned status {resp.status}")
        except Exception as e:
            raise Exception(
                f"Failed to fetch hydrological observations for {station_code}: {e}"
            ) from e

    async def get_hydro_observation_data(
        self, station_code: str, observation_type: str, date: str = "latest"
    ) -> HydroObservationData:
        """Get hydrological observation data for a station.

        Args:
            station_code: The code of the station.
            observation_type: Type of observation ("measured" or "historical").
            date: Date in format YYYY-MM-DD or "latest". For historical, can be YYYY-MM.

        Returns:
            HydroObservationData with observations.
        """
        if not self.session:
            raise Exception("Session not initialized")

        try:
            async with self.session.get(
                f"{self.BASE_URL}/hydro-stations/{station_code}/observations/{observation_type}/{date}"
            ) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    station = HydroStation(
                        code=response["station"].get("code"),
                        name=response["station"].get("name"),
                        water_body=response["station"].get("waterBody"),
                        coordinates=response["station"].get("coordinates", {}),
                    )

                    observations = []
                    for obs_data in response.get("observations", []):
                        observations.append(
                            HydroObservation(
                                observation_time_utc=obs_data.get("observationTimeUtc"),
                                observation_date_utc=obs_data.get("observationDateUtc"),
                                water_level=obs_data.get("waterLevel"),
                                water_temperature=obs_data.get("waterTemperature"),
                                water_discharge=obs_data.get("waterDischarge"),
                            )
                        )

                    return HydroObservationData(
                        station=station,
                        observations_data_range=response.get("observationsDataRange"),
                        observations=observations,
                    )
                else:
                    raise Exception(f"API returned status {resp.status}")
        except Exception as e:
            raise Exception(
                f"Failed to fetch hydrological data for {station_code}/{observation_type}/{date}: {e}"
            ) from e

    async def get_nearest_hydro_station(
        self, latitude: float, longitude: float
    ) -> Optional[HydroStation]:
        """Find the nearest hydrological station to given coordinates.

        Args:
            latitude: Latitude coordinate.
            longitude: Longitude coordinate.

        Returns:
            Nearest HydroStation or None if no stations found.
        """
        try:
            stations = await self.get_hydro_stations()
            if not stations:
                return None

            # Calculate distance using Haversine formula
            def distance(lat1, lon1, lat2, lon2):
                from math import radians, cos, sin, asin, sqrt

                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * asin(sqrt(a))
                km = 6371 * c
                return km

            nearest = min(
                stations,
                key=lambda s: distance(
                    latitude,
                    longitude,
                    s.coordinates.get("latitude", 0),
                    s.coordinates.get("longitude", 0),
                ),
            )
            return nearest
        except Exception as e:
            raise Exception(f"Failed to find nearest hydrological station: {e}") from e

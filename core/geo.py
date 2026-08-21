"""
Geo-distance utilities using the Haversine formula.

We use Haversine instead of PostGIS because our dataset is small
(under 1000 records) and this avoids requiring the GDAL/PostGIS system
dependencies, at negligible cost to accuracy or performance at this scale.
"""

import math

EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two lat/lng points, in kilometers.
    """
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def bounding_box(lat: float, lon: float, radius_km: float) -> dict:
    """
    Compute a rough lat/lng bounding box around a point, for use as a cheap
    pre-filter in a DB query before precise Haversine filtering in Python.

    This is intentionally approximate (doesn't account for longitude
    convergence near the poles) — fine for San Francisco's latitude range.
    """
    lat_delta = radius_km / 111.0  # ~111 km per degree of latitude, roughly constant
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    return {
        "min_lat": lat - lat_delta,
        "max_lat": lat + lat_delta,
        "min_lon": lon - lon_delta,
        "max_lon": lon + lon_delta,
    }

"""
Wrapper for the GeoDB Cities API, see http://geodb-cities-api.wirefreethought.com.
"""

# Maximum radius for querying nearby places
MAX_NEARBY_RADIUS=500_000

from . import models
from .endpoints import (
    find_places, FindPlacesParameters,
    find_city_by_name,
    place_details, PlaceDetailsParameters,
    places_near_place, NearbyPlacesParameters,
)

from dataclasses import dataclass
from functools import cached_property
from typing import Iterator, Optional, TypeVar
import warnings
from apis import APIRequest, APIResponse, Model

from . import models

AnyModel = TypeVar('AnyModel', bound=Model)

class GeoDBApiRequest(APIRequest):

    def __init__(self, path: str, **query_parameters):
        super().__init__(
            "http://geodb-free-service.wirefreethought.com/",
            path,
            **query_parameters
        )

    @cached_property
    def response(self) -> APIResponse:
        return super().response

    def model_list(self, kind: type[AnyModel]) -> list[AnyModel]:
        return super().model_list(kind)

    def model(self, kind: type[AnyModel]) -> AnyModel:
        return super().model(kind)

@dataclass(frozen=True)
class GeoDBApiRequestPager:

    req: GeoDBApiRequest
    max_pages: int = 5
    page_size: int = 10

    def __iter__(self) -> Iterator[models.GenericResponse]:
        req = self.req
        for offset in range(0, self.max_pages * self.page_size, self.page_size):
            parameters = req.parameters | dict(limit=self.page_size, offset=offset)
            req = GeoDBApiRequest(req.path, **parameters)

            res = req.model(models.GenericResponse)
            if res.errors is not None:
                warnings.warn(str(res.errors[0]))
                return
            yield res
            # If the response is not page-able
            if not res.metadata:
                return
            # If we have exhausted the pages
            if res.metadata.currentOffset + len(res.data) >= res.metadata.totalCount:
                return

def find_city_id_by_name(name: str) -> models.ID:
    """Find the city ID corresponding to a city name"""
    req = GeoDBApiRequest(
        '/v1/geo/places',
        namePrefix=name,
        sort=models.SortBy.POPULATION_DEC,
        types=models.PopulatedPlaceType.CITY
    )
    res = models.GenericResponse.fromResponse(req.response)

    assert isinstance(res, models.GenericResponse)
    if res.errors is not None:
        warnings.warn(f"Failed request to GeoDB -- {str(res.errors[0])}")
        return models.null_ID
    if not isinstance(res.data, list):
        warnings.warn("Expected array response")
        return models.null_ID

    return models.PopulatedPlaceSummary.fromResponse(res.data)[0].id

def place_details(id: models.ID) -> Optional[models.PopulatedPlaceDetails]:
    """Get the full details of a place"""
    req = GeoDBApiRequest(
        f'/v1/geo/places/{id}',
    )
    res = models.GenericResponse.fromResponse(req.response)

    assert isinstance(res, models.GenericResponse)
    if res.errors is not None:
        warnings.warn(f"Failed request to GeoDB -- {str(res.errors[0])}")
        return None
    if isinstance(res.data, list):
        warnings.warn("Expected single model response")
        return None

    m = models.PopulatedPlaceDetails.fromResponse(res.data)
    return None if isinstance(m, list) else m

def nearby_cities(near_to: models.ID, radius: float, min_population: int = 40_000) -> list[models.PopulatedPlaceSummary]:
    """
    Find all cities within `radius` (in m) of the specified city ID
    """
    MAX_RADIUS = 500_000
    if radius > MAX_RADIUS:
        warnings.warn(f"[nearby_cities] Reducing search radius from {radius:.0f} to {MAX_RADIUS:.0f}")
        radius = MAX_RADIUS
    req = GeoDBApiRequest(
        f'/v1/geo/places/{near_to}/nearbyPlaces',
        radius=radius / 1000,
        distanceUnit="KM",
        types=models.PopulatedPlaceType.CITY,
        sort=models.SortBy.POPULATION_DEC,
        minPopulation=min_population,
    )
    places = []
    for res in GeoDBApiRequestPager(req, max_pages=3):
        if not isinstance(res.data, list): return places
        places = places + [models.PopulatedPlaceSummary.fromResponse(d) for d in res.data]
    return places

def cities_near_location(lat: float, lon: float, radius: float, min_population: int = 40_000) -> list[models.PopulatedPlaceSummary]:
    """
    Find all cities within `radius` (in m) of the specified coordinates
    """
    MAX_RADIUS = 500_000
    if radius > MAX_RADIUS:
        warnings.warn(f"[nearby_cities] Reducing search radius from {radius:.0f} to {MAX_RADIUS:.0f}")
        radius = MAX_RADIUS
    parse_coord = lambda coord: ('+' if coord >= 0 else '') + f'{coord:.4f}'
    req = GeoDBApiRequest(
        f'/v1/geo/locations/{parse_coord(lat)}{parse_coord(lon)}/nearbyPlaces',
        radius=radius / 1000,
        distanceUnit="KM",
        types=models.PopulatedPlaceType.CITY,
        sort=models.SortBy.POPULATION_DEC,
        minPopulation=min_population,
    )
    places = []
    for res in GeoDBApiRequestPager(req, max_pages=3):
        if not isinstance(res.data, list): return places
        places = places + [models.PopulatedPlaceSummary.fromResponse(d) for d in res.data]
    return places

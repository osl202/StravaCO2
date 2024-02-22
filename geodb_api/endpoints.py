from dataclasses import dataclass
from typing import Iterator, Optional, Union
from apis import APIRequest, APIRequestParameters, AnyModel

from . import models

class GeoDBApiRequest(APIRequest):
    """A request to GeoDB's API"""
    def __init__(self, path: str, **query_parameters):
        super().__init__(
            "http://geodb-free-service.wirefreethought.com/",
            path,
            **query_parameters
        )

@dataclass(frozen=True)
class GeoDBApiRequestPager:
    """Iterate over the pages sent back from a request to GeoDB's API"""

    req: GeoDBApiRequest

    def iter_models(self, type: type[AnyModel]) -> Iterator[Union[AnyModel, models.Error]]:
        req = self.req
        offset = 0
        page_size = int(req.parameters.get('limit', 10))

        # Iterate pages
        while True:
            parameters = req.parameters | dict(limit=page_size, offset=offset)
            res = models.GenericResponse.fromResponse(GeoDBApiRequest(req.path, **parameters).response)

            # Stop if we don't get a valid response
            if res is None or isinstance(res, list) or res.metadata is None:
                err = models.Error(models.ErrorCode.INVALID_RESPONSE, "Invalid response")
                err.warn()
                yield err
                raise StopIteration

            # Stop if the API returns an error
            if res.errors:
                res.errors[0].warn()
                yield res.errors[0]
                raise StopIteration

            # Stop if we didn't get a list of models
            if not isinstance(res.data, list):
                err = models.Error(models.ErrorCode.INVALID_RESPONSE, "Expected array response")
                err.warn()
                yield err
                raise StopIteration

            if res.metadata.totalCount == 0:
                err = models.Error(models.ErrorCode.INVALID_RESPONSE, "No items in response")
                err.warn()
                yield err
                raise StopIteration

            # Iterate models in page
            for m in type.fromResponse(res.data):
                yield m

            # If the response is not page-able
            if not res.metadata: raise StopIteration
            # If we have exhausted the pages
            if res.metadata.currentOffset + len(res.data) >= res.metadata.totalCount: raise StopIteration

            offset += page_size


@dataclass(frozen=True)
class NearbyPlacesParameters(APIRequestParameters):
    """
    :param radius: The location radius within which to find places
    :param distanceUnit: The unit of distance
    :param countryIds: Only places in these countries
    :param excludedCountryIds: Only places NOT in these countries
    :param minPopulation: Only places having at least this population
    :param maxPopulation: Only places having no more than this population
    :param namePrefix: Only entities whose names start with this prefix. If languageCode is set, the prefix will be matched on the name as it appears in that language
    :param namePrefixDefaultLangResults: When name-prefix matching, whether or not to match on names in the default language if a non-default languageCode is set
    :param timeZoneIds: Only places in these time-zones
    :param types: Only places for these types
    :param asciiMode: Display results using ASCII characters
    :param hateoasMode: Include HATEOAS-style links in results
    :param languageCode: Display results in this language
    :param limit: The maximum number of results to retrieve
    :param offset: The zero-ary offset index into the results
    :param sort: How to sort places
    :param includeDeleted: Whether to include any divisions marked deleted
    """
    radius: Optional[int] = None
    distanceUnit: models.DistanceUnit = models.DistanceUnit.KM
    countryIds: Optional[list[str]] = None
    excludedCountryIds: Optional[list[str]] = None
    minPopulation: Optional[int] = None
    maxPopulation: Optional[int] = None
    namePrefix: Optional[str] = None
    namePrefixDefaultLangResults: bool = True
    timeZoneIds: Optional[list[str]] = None
    types: Optional[list[models.PopulatedPlaceType]] = None
    asciiMode: bool = False
    hateoasMode: bool = True
    languageCode: Optional[str] = None
    limit: int = 10
    offset: int = 0
    sort: Optional[models.SortBy] = None
    includeDeleted: models.DeletedType = models.DeletedType.NONE

def places_near_place(place: models.ID, params: NearbyPlacesParameters, max_results: int) -> list[Union[models.PopulatedPlaceSummary, models.Error]]:
    """
    Find places near the given place, filtering by optional criteria.
    If no criteria are set, you will get back all places within the default radius.
    """
    req = GeoDBApiRequest(
        f'/v1/geo/places/{place}/nearbyPlaces',
        **params.as_dict() | dict(limit=min(params.limit, max_results))
    )
    pager = GeoDBApiRequestPager(req)
    places = []
    for i, p in enumerate(pager.iter_models(models.PopulatedPlaceSummary)):
        places.append(p)
        if i >= max_results - 1 or isinstance(p, models.Error):
            break
    return places


@dataclass(frozen=True)
class FindPlacesParameters(NearbyPlacesParameters):
    """
    :param location: Only places near this location
    :param radius: The location radius within which to find places
    :param distanceUnit: The unit of distance
    :param countryIds: Only places in these countries
    :param excludedCountryIds: Only places NOT in these countries
    :param minPopulation: Only places having at least this population
    :param maxPopulation: Only places having no more than this population
    :param namePrefix: Only entities whose names start with this prefix. If languageCode is set, the prefix will be matched on the name as it appears in that language
    :param namePrefixDefaultLangResults: When name-prefix matching, whether or not to match on names in the default language if a non-default languageCode is set
    :param timeZoneIds: Only places in these time-zones
    :param types: Only places for these types
    :param asciiMode: Display results using ASCII characters
    :param hateoasMode: Include HATEOAS-style links in results
    :param languageCode: Display results in this language
    :param limit: The maximum number of results to retrieve
    :param offset: The zero-ary offset index into the results
    :param sort: How to sort places
    :param includeDeleted: Whether to include any divisions marked deleted
    """
    location: Optional[models.LatLong] = None

def find_places(params: FindPlacesParameters, max_results: int) -> list[Union[models.PopulatedPlaceSummary, models.Error]]:
    """Find places, filtering by optional criteria. If no criteria are set, you will get back all known places"""
    req = GeoDBApiRequest(
        f'/v1/geo/places',
        **params.as_dict() | dict(limit=min(params.limit, max_results))
    )
    pager = GeoDBApiRequestPager(req)
    places = []
    for i, p in enumerate(pager.iter_models(models.PopulatedPlaceSummary)):
        places.append(p)
        if i >= max_results - 1 or isinstance(p, models.Error):
            break
    return places

def find_city_by_name(name: str) -> Union[models.PopulatedPlaceSummary, models.Error]:
    """Find the city ID corresponding to a city name"""
    params = FindPlacesParameters(namePrefix=name, types=[models.PopulatedPlaceType.CITY])
    place = find_places(params, max_results=1)[0]
    if isinstance(place, models.Error): return place
    return place


@dataclass(frozen=True)
class PlaceDetailsParameters(APIRequestParameters):
    """
    :param asciiMode: Display results using ASCII characters
    :param languageCode: Display results in this language
    """
    asciiMode: bool = False
    languageCode: Optional[str] = None

def place_details(placeId: models.ID, params: PlaceDetailsParameters = PlaceDetailsParameters()) -> Union[models.PopulatedPlaceDetails, models.Error]:
    """Get place details such as location coordinates, population, and elevation above sea-level (if available)"""
    req = GeoDBApiRequest(
        f'/v1/geo/places/{placeId}',
        **params.as_dict()
    )
    res = models.GenericResponse.fromResponse(req.response)

    # GeoDB should always return dictionaries rather than lists
    assert isinstance(res, models.GenericResponse)

    # Check for any errors
    if res.errors is not None:
        res.errors[0].warn()
        return res.errors[0]

    # Make sure the data is a single result
    if isinstance(res.data, list):
        err = models.Error(models.ErrorCode.INVALID_RESPONSE, "Expected object response, received array")
        err.warn()
        return err

    return models.PopulatedPlaceDetails.fromResponse(res.data)


def place_distance(src: models.ID, dest: models.ID, distanceUnit: models.DistanceUnit = models.DistanceUnit.KM) -> Union[float, models.Error]:
    req = GeoDBApiRequest(
        f'/v1/geo/places/{src}/distance',
        **dict(toPlaceId=dest, distanceUnit=distanceUnit)
    )
    res = models.GenericResponse.fromResponse(req.response)

    # GeoDB should always return dictionaries rather than lists
    assert isinstance(res, models.GenericResponse)

    # Check for any errors
    if res.errors is not None:
        res.errors[0].warn()
        return res.errors[0]

    # Make sure the data is a single result
    if isinstance(res.data, list):
        err = models.Error(models.ErrorCode.INVALID_RESPONSE, "Expected object response, received array")
        err.warn()
        return err

    return float(res.data) # type: ignore The API returns just a single float

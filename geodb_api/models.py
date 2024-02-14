"""
Response models from GeoDB Cities, taken from
https://wirefreethought.github.io/geodb-cities-api-docs/.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Any, NewType, Optional
import warnings
from apis import Model, APIResponse

ID = NewType('ID', int)
null_ID = ID(-1)


class ErrorCode(StrEnum):
    """All possible error codes returned by the API"""
    ACCESS_DENIED="ACCESS_DENIED"
    ENTITY_NOT_FOUND="ENTITY_NOT_FOUND"
    INCOMPATIBLE="INCOMPATIBLE"
    PARAM_INVALID="PARAM_INVALID"
    PARAMS_MUTUALLY_EXCLUSIVE="PARAMS_MUTUALLY_EXCLUSIVE"
    REQUEST_UNPROCESSABLE="REQUEST_UNPROCESSABLE"

    INVALID_RESPONSE="INVALID_RESPONSE"

class SortBy(StrEnum):
    COUNTRY_ASC="+countryCode"
    COUNTRY_DEC="-countryCode"
    ELEVATION_ASC="+elevation"
    ELEVATION_DEC="-elevation"
    NAME_ASC="+name"
    NAME_DEC="-name"
    POPULATION_ASC="+population"
    POPULATION_DEC="-population"

class DistanceUnit(StrEnum):
    """Units for distances in queries to the API"""
    KM="KM"
    MI="MI"

class DeletedType(StrEnum):
    """Include divisions marked deleted"""
    ALL="ALL"
    NONE="NONE"
    SINCE_YESTERDAY="SINCE_YESTERDAY"
    SINCE_LAST_WEEK="SINCE_LAST_WEEK"

class PopulatedPlaceType(StrEnum):
    """Enumerated types of places returned by the API"""
    ADM2="ADM2"
    CITY="CITY"
    ISLAND="ISLAND"


@dataclass(frozen=True)
class Error(Model):
    """Error returned by the API"""
    code: ErrorCode
    message: str

    def __str__(self) -> str:
        return f'{self.code}: {self.message}'

    def warn(self):
        warnings.warn(f"[GeoDB] Error {self.code} {self.message}")

    @classmethod
    def parse_field(cls, key: str, value: Any): return str(value)

@dataclass(frozen=True)
class Link(Model):
    """Link to another page of results, returned by the API"""
    href: str
    rel: str

    @classmethod
    def parse_field(cls, key: str, value: Any): return str(value)

@dataclass(frozen=True)
class Metadata(Model):
    """Metadata about the number of results in the API response"""
    currentOffset: int
    totalCount: int

    @classmethod
    def parse_field(cls, key: str, value: Any): return int(value)

@dataclass(frozen=True)
class GenericResponse(Model):
    """
    Response from the API containing `errors`, `links`, `metadata`,
    and `data`. `data` contains the unparsed data, which should be
    parsed into a model.
    """
    data: APIResponse
    errors: Optional[list[Error]]
    links: Optional[list[Link]]
    metadata: Optional[Metadata] = None

    @classmethod
    def parse_field(cls, key: str, value: Any):
        if key == 'errors':
            return [Error.fromResponse(x) for x in value]
        elif key == 'links':
            return [Link.fromResponse(x) for x in value]
        elif key == 'metadata':
            return Metadata.fromResponse(value)
        else:
            return value

@dataclass(frozen=True)
class LatLong:
    """An ISO-6709 latitude + longitude"""
    latitude: float
    longitude: float

    def __str__(self) -> str:
        parse_coord = lambda coord: ('+' if coord >= 0 else '') + f'{coord:.4f}'
        return parse_coord(self.latitude) + parse_coord(self.longitude)

    @classmethod
    def from_str(cls, s: str) -> LatLong:
        matches = [float(x) for x in re.findall('[+|-][0-9]+\.[0-9]+', s)]
        if len(matches) != 2:
            warnings.warn("Invalid latitude-longitude string")
            return LatLong(0, 0)
        return LatLong(*matches)

@dataclass(frozen=True)
class PopulatedPlaceSummary(Model):
    """
    Summary of a place. Returned by the API for endpoints
    that return a list of places.
    """
    country: str
    countryCode: str
    id: ID
    latitude: float
    longitude: float
    name: str
    population: Optional[int]
    region: str
    regionCode: str
    regionWdId: Optional[str]
    type: PopulatedPlaceType
    wikiDataId: str
    distance: Optional[float]
    """Inlcuded if this is the result of a distance query"""

    @classmethod
    def parse_field(cls, key: str, value: Any) -> Any:
        return value

@dataclass(frozen=True)
class PopulatedPlaceDetails(Model):
    """
    Full populated-place details.
    """
    city: str
    country: str
    countryCode: str
    deleted: bool
    id: ID
    latitude: float
    longitude: float
    name: str
    population: int
    region: str
    regionCode: str
    regionWdId: str
    timezone: str
    type: PopulatedPlaceType
    wikiDataId: str
    elevationMeters: Optional[int]

    @classmethod
    def parse_field(cls, key: str, value: Any) -> Any:
        return value


from dataclasses import dataclass
import dataclasses
from functools import cached_property
from typing import Any, TypeVar

import requests
from .response import APIResponse, Model

AnyModel = TypeVar('AnyModel', bound=Model)

@dataclass(frozen=True)
class APIRequestParameters:
    def as_dict(self) -> dict[str, Any]:
        keys = tuple(f.name for f in dataclasses.fields(self))
        d = {k: getattr(self, k) for k in keys if getattr(self, k) is not None}
        return d

class APIRequest:
    """An API request with query parameters"""

    base_url: str
    path: str
    headers: dict[str, str]
    parameters: dict[str, str]

    def __init__(self, base_url: str, path: str, headers: dict[str, str] = {}, **query_parameters):
        self.base_url = base_url
        self.path = path
        self.headers = headers
        self.parameters = {
            k: ','.join([str(x) for x in v]) if isinstance(v, list) else str(v)
            for k, v in query_parameters.items()
        }

    @property
    def url(self) -> str:
        """The complete URL of the API request"""
        return self.base_url + self.path

    @cached_property
    def _res(self) -> requests.Response:
        return requests.get(self.url, params=self.parameters, headers=self.headers)

    @cached_property
    def response(self) -> APIResponse:
        """Fetches from the API and converts to a JSON dict"""
        self._res.status_code
        print(f"API request to '{self._res.url}'")
        return self._res.json()

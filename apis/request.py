from dataclasses import dataclass
import dataclasses
from functools import cached_property
from typing import Any, Optional, TypeVar
import warnings

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
    def response(self) -> APIResponse:
        """Fetches from the API and converts to a JSON dict"""
        req = requests.get(self.url, params=self.parameters, headers=self.headers)
        print(f"API request to '{req.url}'")
        return req.json()

    def model_list(self, kind: type[AnyModel]) -> list[AnyModel]:
        """Converts the API response into a list of models, returns an empty list if not possible"""
        if not isinstance(self.response, list):
            warnings.warn("API call recieved a single model where a list of models was expected.")
            return []
        return [kind.fromResponse(r) for r in self.response]

    def model(self, kind: type[AnyModel]) -> Optional[AnyModel]:
        """Fetches from the API and converts to the specified model, returns an empty model if not possible"""
        if isinstance(self.response, list):
            warnings.warn("API call recieved a list of models where a single model was expected.")
            return None
        return kind.fromResponse(self.response)

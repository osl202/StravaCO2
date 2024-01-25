from functools import cached_property
from typing import TypeVar
import warnings

import requests
from .response import APIResponse, Model

AnyModel = TypeVar('AnyModel', bound=Model)

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
        self.parameters = {k: str(query_parameters[k]) for k in query_parameters}

    @property
    def url(self) -> str:
        """The complete URL of the API request"""
        return self.base_url + self.path + '?' + '&'.join([f'{k}={self.parameters[k]}' for k in self.parameters])

    @cached_property
    def response(self) -> APIResponse:
        """Fetches from the API and converts to a JSON dict"""
        return requests.get(self.url, headers=self.headers).json()

    def model_list(self, kind: type[AnyModel]) -> list[AnyModel]:
        """Converts the API response into a list of models, returns an empty list if not possible"""
        if not isinstance(self.response, list):
            warnings.warn("API call recieved a single model where a list of models was expected.")
            return []
        return [kind.fromResponse(r) for r in self.response]

    def model(self, kind: type[AnyModel]) -> AnyModel:
        """Fetches from the API and converts to the specified model, returns an empty model if not possible"""
        if isinstance(self.response, list):
            warnings.warn("API call recieved a list of models where a single model was expected.")
            return kind.fromResponse({})
        return kind.fromResponse(self.response)

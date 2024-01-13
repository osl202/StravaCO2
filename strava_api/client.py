from __future__ import annotations
from typing import Optional
import warnings
import requests
from functools import cached_property
from .oauth import OAuthTokens
from . import models
from . import APIResponse

class Client:
    """An authenticated Strava user"""

    tokens: OAuthTokens
    api_calls: int = 0 # Track total number of API calls for this client

    def __init__(self, tokens: OAuthTokens):
        self.tokens = tokens

    @classmethod
    def from_refresh(cls, refresh_token: Optional[str]) -> Optional[Client]:
        if not refresh_token: return
        tokens = OAuthTokens.from_refresh(refresh_token)
        if not tokens: return
        return Client(tokens)

    @classmethod
    def from_code(cls, auth_code: Optional[str]) -> Optional[Client]:
        if not auth_code: return
        tokens = OAuthTokens.from_code(auth_code)
        if not tokens: return
        return Client(tokens)

    def deauthorize(self):
        if self.tokens:
            self.tokens.deauthorize()

    # Properties are cached to avoid duplicate API calls

    @cached_property
    def use_metric(self) -> bool:
        """Whether to display measurements in metric or imperial units"""
        return self.athlete.measurement_preference != 'feet'

    @cached_property
    def athlete(self) -> models.Athlete:
        return APIRequest(self, '/athlete').model(models.Athlete)

    @cached_property
    def activity_stats(self) -> models.ActivityStats:
        return APIRequest(self, f"/athletes/{self.athlete.id}/stats").model(models.ActivityStats)

    @cached_property
    def activities(self) -> list[models.SummaryActivity]:
        return PagedAPIRequest(self, '/athlete/activities').model_list(models.SummaryActivity)


class APIRequest:
    """An API request with query parameters"""

    client: Client
    path: str
    parameters: dict[str, str]

    def __init__(self, client: Client, path: str, **query_parameters):
        self.client = client
        self.path = path
        self.parameters = {k: str(query_parameters[k]) for k in query_parameters}

    @property
    def url(self) -> str:
        """The complete URL of the API request"""
        base_url = "https://www.strava.com/api/v3/"
        return base_url + self.path + '?' + '&'.join([f'{k}={self.parameters[k]}' for k in self.parameters])

    @cached_property
    def response(self) -> APIResponse:
        """Fetches from the API and converts to a JSON dict"""
        self.client.api_calls += 1
        return requests.get(self.url, headers={'Authorization': f'Bearer {self.client.tokens.access}'}).json()

    def model_list(self, kind: type[models.AnyModel]) -> list[models.AnyModel]:
        """Converts the API response into a list of models, returns an empty list if not possible"""
        if not isinstance(self.response, list):
            warnings.warn("API call recieved a single model where a list of models was expected.")
            return []
        return [kind.fromResponse(r) for r in self.response]

    def model(self, kind: type[models.AnyModel]) -> models.AnyModel:
        """Fetches from the API and converts to the specified model, returns an empty model if not possible"""
        if isinstance(self.response, list):
            warnings.warn("API call recieved a list of models where a single model was expected.")
            return kind.fromResponse({})
        return kind.fromResponse(self.response)


class PagedAPIRequest(APIRequest):
    """An API request that gives paged results"""

    per_page: int
    page: int

    def __init__(self, client: Client, path: str, per_page: int = 30, page: int = 1, **query_parameters):
        super().__init__(client, path, page=page, per_page=per_page, **query_parameters)

    def next(self):
        """Create API request for next page"""
        return PagedAPIRequest(self.client, self.path, self.per_page, self.page + 1, **self.parameters)

    def previous(self):
        """Create API request for previous page"""
        return PagedAPIRequest(self.client, self.path, self.per_page, self.page + 1, **self.parameters)

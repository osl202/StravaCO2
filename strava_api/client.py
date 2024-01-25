from __future__ import annotations
from typing import Optional
from functools import cached_property
from .oauth import OAuthTokens
from apis import APIRequest, APIResponse

from . import models

class StravaAPIRequest(APIRequest):

    client: Client

    def __init__(self, client: Client, path: str, **query_parameters):
        super().__init__(
            "https://www.strava.com/api/v3/",
            path,
            {'Authorization': f'Bearer {client.tokens.access}'},
            **query_parameters
        )
        self.client = client

    @cached_property
    def response(self) -> APIResponse:
        self.client.api_calls += 1
        return super().response


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
        return StravaAPIRequest(self, '/athlete').model(models.Athlete)

    @cached_property
    def activity_stats(self) -> models.ActivityStats:
        return StravaAPIRequest(self, f"/athletes/{self.athlete.id}/stats").model(models.ActivityStats)

    @cached_property
    def activities(self) -> list[models.SummaryActivity]:
        return StravaAPIRequest(self, '/athlete/activities', page=1, per_page=30).model_list(models.SummaryActivity)


# class StravaPagedAPIRequest(StravaAPIRequest):
#     """An API request that gives paged results"""

#     per_page: int
#     page: int

#     def __init__(self, client: Client, path: str, per_page: int = 30, page: int = 1, **query_parameters):
#         super().__init__(client, path, page=page, per_page=per_page, **query_parameters)

#     def next(self):
#         """Create API request for next page"""
#         return StravaPagedAPIRequest(self.client, self.path, self.per_page, self.page + 1, **self.parameters)

#     def previous(self):
#         """Create API request for previous page"""
#         return StravaPagedAPIRequest(self.client, self.path, self.per_page, self.page + 1, **self.parameters)

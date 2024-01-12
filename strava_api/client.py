import requests
from functools import cached_property
from .oauth import OAuthTokens
from . import models

class Client:
    """An authenticated Strava user"""

    tokens: OAuthTokens
    api_calls: int = 0 # Track total number of API calls for this client

    def __init__(self, tokens: OAuthTokens):
        self.tokens = tokens

    def _make_api_request(self, path) -> dict:
        self.api_calls += 1
        base_url = "https://www.strava.com/api/v3/"
        return requests.get(base_url + path, headers={'Authorization': f'Bearer {self.tokens.access}'}).json()

    # Properties are cached to avoid duplicate API calls

    @cached_property
    def use_metric(self) -> bool:
        """Whether to display measurements in metric or imperial units"""
        return self.athlete.measurement_preference != 'feet'

    @cached_property
    def athlete(self) -> models.Athlete:
        json = self._make_api_request('/athlete')
        return models.Athlete.fromJSON(json)

    @cached_property
    def activity_stats(self) -> models.ActivityStats:
        json = self._make_api_request(f"/athletes/{self.athlete.id}/stats")
        return models.ActivityStats.fromJSON(json)

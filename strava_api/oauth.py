from __future__ import annotations
import os
from typing import Optional
import urllib.parse
import requests
from dataclasses import dataclass

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# The url to send the user to if they ask to connect their Strava account
connect_url = "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode({
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'redirect_uri': 'http://localhost:5000/authorize',
    'scope': 'read,profile:read_all,activity:read_all',
})

@dataclass(frozen=True)
class OAuthTokens:
    """A pair of two tokens for the Strava OAuth2: an access token and a refresh token"""

    access: str
    refresh: str

    def deauthorize(self) -> None:
        """De-authorize the current user (i.e. log out)"""
        requests.post("https://www.strava.com/api/v3/oauth/deauthorize", data={
            'access_token': self.access,
        })

    @classmethod
    def from_refresh(cls, refresh_token) -> Optional[OAuthTokens]:
        """
        Given a refresh token from the client, we can obtain the new access and refresh tokens.
        """
        req = requests.post("https://www.strava.com/api/v3/oauth/token", data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        })
        res = req.json()
        if req.status_code != 200: return
        return cls(res['access_token'], res['refresh_token'])


    @classmethod
    def from_code(cls, auth_code) -> Optional[OAuthTokens]:
        """
        Given an authorization code from Strava, we can obtain the access and refresh tokens
        that allow us to access the user's data.
        """
        req = requests.post("https://www.strava.com/api/v3/oauth/token", data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code,
            'grant_type': 'authorization_code',
        })
        if req.status_code != 200: return
        res = req.json()
        return cls(res['access_token'], res['refresh_token'])


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

    # @cached_property
    # def use_metric(self) -> bool:
    #     """Whether to display measurements in metric or imperial units"""
    #     return self.athlete.measurement_preference != 'feet'

    # @cached_property
    # def athlete(self) -> models.Athlete:
    #     return StravaAPIRequest(self, '/athlete').model(models.Athlete)

    # @cached_property
    # def activity_stats(self) -> models.ActivityStats:
    #     return StravaAPIRequest(self, f"/athletes/{self.athlete.id}/stats").model(models.ActivityStats)

    # @cached_property
    # def activities(self) -> list[models.SummaryActivity]:
    #     return StravaAPIRequest(self, '/athlete/activities', page=1, per_page=30).model_list(models.SummaryActivity)


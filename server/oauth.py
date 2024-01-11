import os
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
    'scope': 'read',
})

@dataclass(frozen=True)
class OAuthTokens:

    access: str
    refresh: str

    def deauthorize(self) -> None:
        req = requests.post("https://www.strava.com/api/v3/oauth/token", data={
            'access_token': self.access,
        })

    @classmethod
    def from_refresh(cls, refresh_token) -> 'OAuthTokens':
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
        return cls(res['access_token'], res['refresh_token'])


    @classmethod
    def from_code(cls, code) -> 'OAuthTokens':
        """
        Given an authorization code from Strava, we can obtain the access and refresh tokens
        that allow us to access the user's data.
        """
        req = requests.post("https://www.strava.com/api/v3/oauth/token", data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
        })
        res = req.json()
        return cls(res['access_token'], res['refresh_token'])

"""
Wrapper for the Strava API.
Contains classes to obtain auth tokens in `.oauth`, and to parse responses from the API in `.models`.
Start by initialising a `Client` using `OAuthTokens`.
"""

from .oauth import connect_url, Client
from . import models
from .endpoints import (
    get_athlete,
    get_athlete_activities,
    get_athlete_stats,
)

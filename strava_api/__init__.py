"""
Wrapper for the Strava API.
Contains classes to obtain auth tokens in `.oauth`, and to parse responses from the API in `.models`.
Start by initialising a `Client` using `OAuthTokens`.
"""

from typing import Any, Union
APIResponse = Union[dict[str, Any], list[Any]]

from .client import Client
from .oauth import OAuthTokens, connect_url

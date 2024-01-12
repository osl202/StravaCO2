"""
Models from https://developers.strava.com/docs/reference/#api-models,
defining the format of API responses. Every API request to strava returns
data in the format of a 'model', which is just a data structure with
a load of attributes.
"""

from dataclasses import dataclass
from datetime import datetime
from inspect import signature
from abc import ABC
from typing import Optional

class Model(ABC):
    """A Strava API response model"""

    @classmethod
    def fromJSON(cls, json: dict):
        """Initialises the model with keys from a dict by matching key and parameter names"""
        # Filter the JSON keys to those defined in the model
        keys = list(signature(cls.__init__).parameters.keys())[1:]
        # Set fields not in the JSON to None
        return cls(**{k: json[k] if k in json else None for k in keys})

@dataclass(frozen=True)
class Athlete(Model):
    id: int                                 # The unique identifier of the athlete
    firstname: str                          # The athlete's first name.
    lastname: str                           # The athlete's last name.
    profile_medium: str                     # URL to a 62x62 pixel profile picture.
    profile: str                            # URL to a 124x124 pixel profile picture.
    bio: str                                # The athlete's bio
    city: str                               # The athlete's city.
    state: str                              # The athlete's state or geographical region.
    country: str                            # The athlete's country.
    sex: str                                # The athlete's sex. May take one of the following values: M, F
    summit: bool                            # Whether the athlete has any Summit subscription.
    created_at: datetime                    # The time at which the athlete was created.
    updated_at: datetime                    # The time at which the athlete was last updated.

    # Only present if given more permissions
    username: Optional[str]                 # The athlete's username.
    follower_count: Optional[int]           # The athlete's follower count.
    friend_count: Optional[int]             # The athlete's friend count.
    measurement_preference: Optional[str]   # The athlete's preferred unit system. May take one of the following values: feet, meters
    ftp: Optional[int]                      # The athlete's FTP (Functional Threshold Power).
    weight: Optional[float]                 # The athlete's weight.

    # clubs: SummaryClub                      # The athlete's clubs.
    # bikes: SummaryGear                      # The athlete's bikes.
    # shoes: SummaryGear                      # The athlete's shoes. 

@dataclass(frozen=True)
class ActivityTotal(Model):
    count: int             = 0              # The number of activities considered in this total.
    distance: float        = 0              # The total distance covered by the considered activities.
    moving_time: int       = 0              # The total moving time of the considered activities.
    elapsed_time: int      = 0              # The total elapsed time of the considered activities.
    elevation_gain: float  = 0              # The total elevation gain of the considered activities.
    achievement_count: int = 0              # The total number of achievements of the considered activities. 

@dataclass(frozen=True)
class ActivityStats(Model):
    biggest_ride_distance: float            # The longest distance ridden by the athlete.
    biggest_climb_elevation_gain: float     # The highest climb ridden by the athlete.
    recent_ride_totals: ActivityTotal       # The recent (last 4 weeks) ride stats for the athlete.
    recent_run_totals: ActivityTotal        # The recent (last 4 weeks) run stats for the athlete.
    recent_swim_totals: ActivityTotal       # The recent (last 4 weeks) swim stats for the athlete.
    ytd_ride_totals: ActivityTotal          # The year to date ride stats for the athlete.
    ytd_run_totals: ActivityTotal           # The year to date run stats for the athlete.
    ytd_swim_totals: ActivityTotal          # The year to date swim stats for the athlete.
    all_ride_totals: ActivityTotal          # The all time ride stats for the athlete.
    all_run_totals: ActivityTotal           # The all time run stats for the athlete.
    all_swim_totals: ActivityTotal          # The all time swim stats for the athlete. 

    @classmethod
    def fromJSON(cls, json: dict):
        return super(ActivityStats, cls).fromJSON({
            k: ActivityTotal.fromJSON(json[k]) if k.endswith('_totals') else json[k]
            for k in json
        })

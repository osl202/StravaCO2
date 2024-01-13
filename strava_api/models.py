"""
Models from https://developers.strava.com/docs/reference/#api-models,
defining the format of API responses. Every API request to strava returns
data in the format of a 'model', which is just a data structure with
a load of attributes.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from inspect import signature
from abc import ABC, abstractmethod
from typing import Any, Optional, Self, Tuple, TypeVar, Union, overload
from . import APIResponse

AnyModel = TypeVar('AnyModel', bound='Model')

class Model(ABC):
    """A Strava API response model"""

    @classmethod
    @abstractmethod
    def parse_field(cls, key: str, value: Any) -> Any:
        """
        Decides how each field should be parsed from a provided JSON
        dictionary. This must be implemented for each `Model`.
        """
        raise NotImplementedError()

    @overload
    @classmethod
    def fromResponse(cls, res: list[Any]) -> list[Self]:
        ...
    @overload
    @classmethod
    def fromResponse(cls, res: dict[str, Any]) -> Self:
        ...
    @classmethod
    def fromResponse(cls, res: APIResponse) -> Union[Self, list[Self]]:
        """
        Initialises a model (or list of models) with keys from a dict by matching key
        and parameter names. A derived class will need to initialise non-primitive types
        (e.g. fields that are a `Model` themselves) before passing the JSON.
        """
        if isinstance(res, dict):
            # Filter the JSON keys to those defined in the model
            keys = list(signature(cls.__init__).parameters.keys())[1:]
            # Set fields not in the JSON to None
            return cls(**{k: cls.parse_field(k, res[k]) if k in res else None for k in keys})
        else:
            return [cls.fromResponse(r) for r in res]


@dataclass(frozen=True)
class Athlete(Model):
    """A summary of an athlete. Not all of the fields will be available."""
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

    @classmethod
    def parse_field(cls, key, value) -> Any:
        return (datetime.fromisoformat(value) if key in ['created_at', 'updated_at'] else value)

@dataclass(frozen=True)
class ID(Model):
    """
    Class containing only the ID of the entity it represents. Sometimes returned
    by Strava instead of a full `Athlete` model or similar.
    """
    id: int

    @classmethod
    def parse_field(cls, key: str, value: Any) -> Any:
        return value

@dataclass(frozen=True)
class ActivityTotal(Model):
    """A roll-up of metrics pertaining to a set of activities. Values are in seconds and meters."""
    count: int             = 0              # The number of activities considered in this total.
    distance: float        = 0              # The total distance covered by the considered activities.
    moving_time: int       = 0              # The total moving time of the considered activities.
    elapsed_time: int      = 0              # The total elapsed time of the considered activities.
    elevation_gain: float  = 0              # The total elevation gain of the considered activities.
    achievement_count: int = 0              # The total number of achievements of the considered activities. 

    @classmethod
    def parse_field(cls, key: str, value: Any) -> Any:
        return value

@dataclass(frozen=True)
class ActivityStats(Model):
    """A set of rolled-up statistics and totals for an athlete."""
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
    def parse_field(cls, key: str, value: Any) -> Any:
        return ActivityTotal.fromResponse(value) if key.endswith('_totals') else value

class SportType(StrEnum):
    """An exhaustive list of the possible sports on Strava"""
    AlpineSki="AlpineSki"
    BackcountrySki="BackcountrySki"
    Badminton="Badminton"
    Canoeing="Canoeing"
    Crossfit="Crossfit"
    EBikeRide="EBikeRide"
    Elliptical="Elliptical"
    EMountainBikeRide="EMountainBikeRide"
    Golf="Golf"
    GravelRide="GravelRide"
    Handcycle="Handcycle"
    HighIntensityIntervalTraining="HighIntensityIntervalTraining"
    Hike="Hike"
    IceSkate="IceSkate"
    InlineSkate="InlineSkate"
    Kayaking="Kayaking"
    Kitesurf="Kitesurf"
    MountainBikeRide="MountainBikeRide"
    NordicSki="NordicSki"
    Pickleball="Pickleball"
    Pilates="Pilates"
    Racquetball="Racquetball"
    Ride="Ride"
    RockClimbing="RockClimbing"
    RollerSki="RollerSki"
    Rowing="Rowing"
    Run="Run"
    Sail="Sail"
    Skateboard="Skateboard"
    Snowboard="Snowboard"
    Snowshoe="Snowshoe"
    Soccer="Soccer"
    Squash="Squash"
    StairStepper="StairStepper"
    StandUpPaddling="StandUpPaddling"
    Surfing="Surfing"
    Swim="Swim"
    TableTennis="TableTennis"
    Tennis="Tennis"
    TrailRun="TrailRun"
    Velomobile="Velomobile"
    VirtualRide="VirtualRide"
    VirtualRow="VirtualRow"
    VirtualRun="VirtualRun"
    Walk="Walk"
    WeightTraining="WeightTraining"
    Wheelchair="Wheelchair"
    Windsurf="Windsurf"
    Workout="Workout"
    Yoga="Yoga"

@dataclass(frozen=True)
class SummaryActivity(Model):
    """A summary of a recorded activity"""
    id: int                                 # The unique identifier of the activity
    external_id: str                        # The identifier provided at upload time
    upload_id: int                          # The identifier of the upload that resulted in this activity
    athlete: ID                             # The athlete as only an ID
    name: str                               # The name of the activity
    distance: float                         # The activity's distance, in meters
    moving_time: int                        # The activity's moving time, in seconds
    elapsed_time: int                       # The activity's elapsed time, in seconds
    total_elevation_gain: float             # The activity's total elevation gain.
    elev_high: float                        # The activity's highest elevation, in meters
    elev_low: float                         # The activity's lowest elevation, in meters
    sport_type: SportType                   # An instance of SportType.
    start_date: datetime                    # The time at which the activity was started.
    start_date_local: datetime              # The time at which the activity was started in the local timezone.
    timezone: str                           # The timezone of the activity
    start_latlng: Tuple[float, float]       # An instance of LatLng.
    end_latlng: Tuple[float, float]         # An instance of LatLng.
    achievement_count: int                  # The number of achievements gained during this activity
    kudos_count: int                        # The number of kudos given for this activity
    comment_count: int                      # The number of comments for this activity
    athlete_count: int                      # The number of athletes for taking part in a group activity
    photo_count: int                        # The number of Instagram photos for this activity
    total_photo_count: int                  # The number of Instagram and Strava photos for this activity
    # map: PolylineMap                        # An instance of PolylineMap TODO: IMPLEMENT?
    trainer: bool                           # Whether this activity was recorded on a training machine
    commute: bool                           # Whether this activity is a commute
    manual: bool                            # Whether this activity was created manually
    private: bool                           # Whether this activity is private
    flagged: bool                           # Whether this activity is flagged
    workout_type: int                       # The activity's workout type
    upload_id_str: str                      # The unique identifier of the upload in str format
    average_speed: float                    # The activity's average speed, in meters per second
    max_speed: float                        # The activity's max speed, in meters per second
    has_kudoed: bool                        # Whether the logged-in athlete has kudoed this activity
    hide_from_home: bool                    # Whether the activity is muted
    gear_id: str                            # The id of the gear for the activity
    kilojoules: float                       # The total work done in kilojoules during this activity. Rides only
    average_watts: float                    # Average power output in watts during this activity. Rides only
    device_watts: bool                      # Whether the watts are from a power meter, false if estimated
    max_watts: int                          # Rides with power meter data only
    weighted_average_watts: int             # Similar to Normalized Power. Rides with power meter data only 

    @classmethod
    def parse_field(cls, key: str, value: Any) -> Any:
        if key.startswith('start_date'):
            return datetime.fromisoformat(value)
        elif key.endswith('latlng'):
            return (value[0], value[1])
        elif key == 'athlete':
            return ID(value)
        else:
            return value

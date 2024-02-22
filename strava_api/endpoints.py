from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional, Union
from functools import cached_property
import itertools

from .oauth import Client
from apis import APIRequest, APIResponse, AnyModel

from . import models


def to_single_model(m: Union[AnyModel, list[AnyModel]]) -> Union[AnyModel, models.Fault]:
    if isinstance(m, list):
        return models.Fault([], "Expected single model")
    else:
        return m

def to_model_list(m: Union[AnyModel, list[AnyModel]]) -> Union[list[AnyModel], models.Fault]:
    if isinstance(m, list):
        return m
    else:
        return models.Fault([], "Expected array of models")


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

    @property
    def success(self) -> bool:
        # Test for HTTP status code 200, which means all ok
        return super()._res.status_code == 200


@dataclass(frozen=True)
class StravaAPIRequestPager:
    """Iterate over the pages sent back from a request to Strava's API"""

    req: StravaAPIRequest

    def iter_models(self, type: type[AnyModel]) -> Iterator[Union[AnyModel, models.Fault]]:
        req = self.req
        page = 1
        page_size = req.parameters.get('per_page', 30)

        # Iterate pages
        while True:
            parameters = req.parameters | dict(per_page=page_size, page=page)
            req = StravaAPIRequest(req.client, req.path, **parameters)
            if not req.success:
                fault = models.Fault.fromResponse(req.response)
                if isinstance(fault, list): fault = fault[0]
                if fault.errors and fault.errors[0].field == 'page':
                    return
                fault.warn()
                yield fault
                return

            # Stop if we didn't get a list of models
            res = to_model_list(type.fromResponse(req.response))
            if isinstance(res, models.Fault):
                res.warn()
                yield res
                return

            # Stop iterating if no models are returned
            if len(res) == 0: return

            # Iterate models in page
            for model in res: yield model

            page += 1


def get_athlete(client: Client) -> Union[models.Athlete, models.Fault]:
    """
    Returns the currently authenticated athlete.
    Tokens with profile:read_all scope will receive a detailed athlete
    representation; all others will receive a summary representation.
    """
    req = StravaAPIRequest(client, '/athlete')
    athlete = to_single_model(models.Athlete.fromResponse(req.response))
    if isinstance(athlete, models.Fault):
        athlete.warn()
    return athlete


def get_athlete_activities(
    client: Client,
    before: Optional[datetime] = None,
    after: Optional[datetime] = None,
    per_page: int = 30,
    max_results: int = 30
) -> Union[list[models.SummaryActivity], models.Fault]:
    """
    Returns the activities of an athlete for a specific identifier.
    Requires activity:read. Only Me activities will be filtered out
    unless requested by a token with activity:read_all.
    :param before: Timestamp to use for filtering activities that have taken place before a certain time.
    :param after: Timestamp to use for filtering activities that have taken place after a certain time.
    """
    req = StravaAPIRequest(
        client,
        '/athlete/activities',
        before=int(datetime.today().timestamp()) if before is None else int(before.timestamp()),
        after=0 if after is None else int(after.timestamp()),
        per_page=min(per_page, max_results)
    )
    pager = StravaAPIRequestPager(req)
    results = list(itertools.islice(pager.iter_models(models.SummaryActivity), max_results))
    for r in results:
        if isinstance(r, models.Fault): return r
    return results # type: ignore results will not contain Faults here


def get_athlete_stats(
    client: Client,
    id: models.ID
) -> Union[models.ActivityStats, models.Fault]:
    """
    Returns the activity stats of an athlete.
    Only includes data from activities set to Everyone visibilty.
    :param id: The identifier of the athlete. Must match the authenticated athlete.
    """
    req = StravaAPIRequest(client, f'/athletes/{id}/stats')
    stats = to_single_model(models.ActivityStats.fromResponse(req.response))
    if isinstance(stats, models.Fault):
        stats.warn()
    return stats

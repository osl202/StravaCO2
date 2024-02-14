import dataclasses
from random import randint

import dash
from flask import request
import plotly.graph_objects as go
import strava_api as api
from strava_api.models import SportType
import geodb_api as geodb
from urllib.parse import parse_qs

NAME = __name__.split('.')[-1]
dash.register_page(__name__)
layout = dash.dcc.Loading(children=[
    dash.dcc.Location(id='url', refresh=False),
    dash.dcc.Geolocation(id="geolocation"),
    dash.html.P(id='travelled-to-place-name'),
    dash.dcc.Graph(id=NAME, config=dict(displayModeBar=False)),
], className='plot-container')

# Save the destination globally so we can update the paragraph element to show its name
desc_text: str = ""

@dash.callback(
    dash.Output(NAME, 'figure'),
    dash.Input('url', 'search'),
    dash.Input("geolocation", "position"),
    prevent_initial_call=True,
)
def update(s: str, location = None):
    
    global desc_text

    args = parse_qs(s.replace('?', ''))
    sport = ''.join(args.get('sport', ['']))

    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client:
        # The user hasn't authorized, can't plot
        return dash.no_update

    fallback_places = [
        "London",
        "Madrid",
        "Paris",
        "Berlin",
        "Athens",
        "New York",
        "Chicago",
        "Los Angeles",
        "Toronto",
    ]

    # For the starting city, first try using the user's current location.
    user_city = geodb.models.Error(geodb.models.ErrorCode.ENTITY_NOT_FOUND, "")
    if location and location.get('lat') and location.get('lon'):
        user_city = geodb.find_places(
            geodb.FindPlacesParameters(
                location=geodb.models.LatLong(location.get('lat'), location.get('lon')),
                radius=100,
                types=[geodb.models.PopulatedPlaceType.CITY],
            ),
            max_results=1
        )[0]

    # If the location isn't available, see if the user has a location on their
    # Strava profile. Fall back to randomly selecting from a few big cities.
    if isinstance(user_city, geodb.models.Error):
        user_city = geodb.find_city_by_name(
            client.athlete.city
            or fallback_places[randint(0, len(fallback_places) - 1)]
        )

    # Couldn't find any of these cities, nothing we can do
    if isinstance(user_city, geodb.models.Error):
        raise dash.exceptions.PreventUpdate

    # Get the sport from the URL query parameters
    if sport.lower() == SportType.Run.lower():
        total_distance = client.activity_stats.all_run_totals.distance
        verb = "run"
    elif sport.lower() == SportType.Ride.lower():
        total_distance = client.activity_stats.all_ride_totals.distance
        verb = "cycled"
    elif sport.lower() == SportType.Swim.lower():
        total_distance = client.activity_stats.all_swim_totals.distance
        verb = "swum"
    else:
        total_distance = sum([
            client.activity_stats.all_run_totals.distance,
            client.activity_stats.all_ride_totals.distance,
            client.activity_stats.all_swim_totals.distance,
        ])
        verb = "travelled"

    # Find possible destination cities
    # TODO: With distances larger than the country, this might not work well
    search_radius = total_distance * 1.5 / 1000
    if search_radius < geodb.MAX_NEARBY_RADIUS:
        # Find nearby cities to the user's location
        cities = geodb.places_near_place(
            user_city.id,
            geodb.NearbyPlacesParameters(
                radius=int(search_radius),
                sort=geodb.models.SortBy.POPULATION_DEC,
            ),
            max_results=20
        )
    else:
        # If outside the maximum search radius, use the most populous cities in the same country
        cities = geodb.find_places(
            geodb.FindPlacesParameters(
                countryIds=[user_city.countryCode],
                sort=geodb.models.SortBy.POPULATION_DEC,
            ),
            max_results=10
        )
        # Get distances to all the cities
        for i, city in enumerate(cities):
            if isinstance(city, geodb.models.Error): continue
            res = geodb.place_distance(user_city.id, city.id)
            if not isinstance(res, geodb.models.Error):
                cities[i] = dataclasses.replace(city, distance=res)

    # Find the city with a distance nearest to the user's travel distance
    cities = [p for p in cities if not isinstance(p, geodb.models.Error)]
    if not cities: raise dash.exceptions.PreventUpdate
    dest_city = sorted(cities, key=lambda place: abs((place.distance or 0)*1000 - total_distance))[0]
    distance = (dest_city.distance or 0) * 1000
    if not distance: raise dash.exceptions.PreventUpdate

    desc_text = f"You've {verb} {total_distance/distance:.1f}x the distance from {user_city.name} to {dest_city.name}"

    # All's good, create the plot!
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        mode='markers+lines',
        lon=[user_city.longitude, dest_city.longitude],
        lat=[user_city.latitude, dest_city.latitude],
        text=[user_city.name, dest_city.name],
    ))
    fig.update_layout(
        margin={'l':0,'t':0,'b':0,'r':0},
        mapbox={
            'center': {
                'lon': 0.5 * (user_city.longitude + dest_city.longitude),
                'lat': 0.5 * (user_city.latitude + dest_city.latitude),
            },
            'style': "open-street-map",
            'zoom': 1_000_000 // total_distance,
        }
    )

    return fig

@dash.callback(
    dash.Output('travelled-to-place-name', 'children'),
    dash.Input(NAME, 'figure')
)
def update_text(_):
    return desc_text

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
)
def update(s: str, location):
    
    global desc_text

    args = parse_qs(s.replace('?', ''))
    sport = ''.join(args.get('sport', ['']))

    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client:
        # The user hasn't authorized, can't plot
        return

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

    """
    For the starting city, first try using the user's current location.
    If that's not available, see if the user has a location on their
    Strava profile. Fall back to randomly selecting from a few big cities.
    """
    place_id = None
    if location and location.get('lat') and location.get('lon'):
        cities_near_loc = geodb.cities_near_location(
            location.get('lat'), location.get('lon'),
            radius=10_000
        )
        if len(cities_near_loc) > 0:
            place_id = cities_near_loc[0].id

    if not place_id:
        place_id = geodb.find_city_id_by_name(
            client.athlete.city
            or fallback_places[randint(0, len(fallback_places) - 1)]
        )

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

    # TODO: Work out what to do when the distance exceeds the maximum radius permitted by the API
    nearby = geodb.nearby_cities(place_id, total_distance * 2)
    if not nearby: return
    closest = sorted(nearby, key=lambda place: abs((place.distance or 0)*1000 - total_distance), reverse=False)
    distance = (closest[0].distance or 0) * 1000
    if len(closest) == 0:
        return

    src = geodb.place_details(place_id)
    dest = geodb.place_details(closest[0].id)
    if not src or not dest:
        return

    desc_text = f"You've {verb} {total_distance/distance:.1f}x the distance from {src.name} to {dest.name}"

    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        mode='markers+lines',
        lon=[src.longitude, dest.longitude],
        lat=[src.latitude, dest.latitude],
        text=[src.name, dest.name],
    ))
    fig.update_layout(
        margin={'l':0,'t':0,'b':0,'r':0},
        mapbox={
            'center': {
                'lon': 0.5 * (src.longitude + dest.longitude),
                'lat': 0.5 * (src.latitude + dest.latitude),
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

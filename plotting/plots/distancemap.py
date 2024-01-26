from random import randint
from typing import Optional
import dash
from flask import request
import plotly.graph_objects as go
import strava_api as api
import geodb_api as geodb

NAME = __name__.split('.')[-1]
dash.register_page(__name__)
layout = dash.dcc.Loading(children=[
    dash.dcc.Location(id='url', refresh=False),
    dash.html.P(id='travelled-to-place-name'),
    dash.dcc.Graph(id=NAME, config=dict(displayModeBar=False)),
], className='plot-container')

# Save the destination globally so we can update the paragraph element to show its name
desc_text: str = ""

@dash.callback(
    dash.Output(NAME, 'figure'),
    dash.Input('url', 'hash'),
)
def update(_):

    global desc_text

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

    place_id = geodb.find_city_id_by_name(
        client.athlete.city or fallback_places[randint(0, len(fallback_places) - 1)]
    )
    # TODO: Make this show a distance for the selected sport
    total_distance = client.activity_stats.all_run_totals.distance
    # TODO: Make repeated API calls to get place when distance exceeds maximum
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

    desc_text = f"You've run {total_distance/distance:.1f}x the distance from {src.name} to {dest.name}"

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

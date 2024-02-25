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
    dash.dcc.Graph(id=NAME, config=dict(displayModeBar=False)),
], className='plot-container')

# Save the destination globally so we can update the paragraph element to show its name
desc_text: str = ""

@dash.callback(
    dash.Output(NAME, 'figure'),
    dash.Input('url', 'search'),
)
def update(s: str):
    
    global desc_text

    args = parse_qs(s.replace('?', ''))
    sport_str = ''.join(args.get('sport', ['']))
    if sport_str:
        if not sport_str in [s.lower() for s in SportType]:
            print(f"Invalid sport type")
            return dash.no_update

    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client:
        # The user hasn't authorized, can't plot
        return dash.no_update

    activities = api.get_athlete_activities(client, max_results=None)
    if isinstance(activities, api.models.Fault):
        return dash.no_update

    if sport_str:
        activities = [a for a in activities if a.sport_type.lower() == sport_str]

    N = len(activities)
    locations = [geodb.models.LatLong(*a.start_latlng) for a in activities]
    labels = [
        a.name + ' ' + a.start_date_local.strftime('%d %b %H:%M')
        for a in activities
    ]

    # All's good, create the plot!
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        mode='markers',
        lon=[l.longitude for l in locations],
        lat=[l.latitude for l in locations],
        text=labels,
    ))
    fig.update_layout(
        margin={'l':0,'t':0,'b':0,'r':0},
        mapbox={
            'style': "open-street-map",
            'center': {
                'lon': sum(l.longitude for l in locations) / N,
                'lat': sum(l.latitude for l in locations) / N,
            },
        }
    )
    return fig


import dash
from flask import request
import plotly.graph_objects as go
import strava_api as api

dash.register_page(__name__)

# The page layout
# dcc.Location is here just to trigger the update of the graph
layout = dash.html.Div([
    dash.dcc.Location(id='url', refresh=False),
    dash.dcc.Graph(id='timehistogram'),
])

# Function that updates the data on the graph
@dash.callback(
    dash.Output('timehistogram', 'figure'),
    dash.Input('url', 'href'),
)
def update(_):
    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client:
        # The user hasn't authorized
        return

    hours = [
        a.start_date_local.hour for a in client.activities
    ]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=hours,
        xbins=dict(start=0, end=23),
        nbinsx=24,
        name='Start times of all recorded activities'
    ))
    fig.update_layout(dict(
        plot_bgcolor='white',
        xaxis=dict(
            range=[0, 23],
            title='Time of day',
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='black',
            tickmode='array',
            tickvals=tuple(range(24)),
            ticktext=[f'{h:02}:00' for h in range(24)]
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
        )
    ))
    return fig

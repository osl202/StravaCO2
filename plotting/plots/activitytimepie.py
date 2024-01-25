import dash
from flask import request
import plotly.graph_objects as go
import strava_api as api
import numpy as np
from plotting import make_layout

NAME = __name__.split('.')[-1]
dash.register_page(__name__)
layout = make_layout(NAME)

@dash.callback(
    dash.Output(NAME, 'figure'),
    dash.Input('url', 'href'),
)
def update(_):

    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client:
        # The user hasn't authorized, can't plot
        return

    hours = [
        a.start_date_local.hour for a in client.activities
    ]
    hist = np.histogram(hours, range(25))[0]

    # The following question was super helpful for this:
    # https://stackoverflow.com/questions/72595317/is-it-possible-to-generate-a-clock-chart-using-plotly
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=hist,
        offset=0.5,
        customdata=np.arange(24),
        hovertemplate="%{r} activities at %{customdata:02}:00<extra></extra>",
    ))
    fig.update_layout(
        margin=dict(l=20, t=20, r=20, b=20),
        polar=dict(
            hole=0.4,
            bgcolor='#ccc',
            radialaxis=dict(
                showticklabels=False,
                showgrid=False,
            ),
            angularaxis=dict(
                tickvals=np.arange(0, 360, 360/24),
                ticktext=[f'{i:02}' if i % 6 == 0 else '' for i in range(24)],
                direction='clockwise',
                period=24,
            )
        )
    )
    return fig

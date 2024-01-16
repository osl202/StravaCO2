import dash
import numpy as np
import plotly.graph_objects as go
from plotting import make_layout

# Register the page with the server and use the layout defined in `plotting/__init__.py`.
# This should be present in every plotting script, and the name should be unique.
NAME = __name__.split('.')[-1]
dash.register_page(__name__)
layout = make_layout(NAME)

# Function that updates the data on the graph.
# This dash.callback is just so that the plot is updated on page load.
# Make sure you change 'example' here to the unique plot name you used above.
@dash.callback(
    dash.Output(NAME.split('.')[-1], 'figure'),
    dash.Input('url', 'href'),
)
def update(_):
    # This is the part of the script where you put your plotting code, returning a plotly figure.

    # Plot a simple sine curve
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
    fig = go.Figure(data=go.Scatter(x=x, y=y))
    return fig


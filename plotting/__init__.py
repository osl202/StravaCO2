import dash
from dash import Dash

def make_layout(unique_plot_name: str):
    # Bare-bones page layout to display and update the plot
    return dash.dcc.Loading(children=[
        dash.dcc.Location(id='url', refresh=False),
        dash.dcc.Graph(id=unique_plot_name, config=dict(displayModeBar=False)),
    ], className='plot-container')

app = Dash(__name__, use_pages=True, pages_folder='plots/', server=False, url_base_pathname='/plots/')
app.layout = dash.page_container

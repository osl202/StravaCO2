import dash
from dash import Dash

app = Dash(__name__, use_pages=True, pages_folder='plots/', server=False, url_base_pathname='/plots/')
app.layout = dash.page_container

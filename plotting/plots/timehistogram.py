import dash
from dash import ClientsideFunction, Input, Output, clientside_callback, html, dcc

dash.register_page(__name__)

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Graph(id='graph')
])

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name=__name__
    ),
    Output('graph', 'figure'),
    Input('url', 'href'),
)

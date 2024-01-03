import strava_api
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import smplotlib
import plotly.express as px
import plotly.graph_objects as go
import polyline

df_strava = pd.DataFrame(strava_api.load_data())

distance = df_strava['distance']
start_date = df_strava['start_date']
end_latlon = df_strava['end_latlng']

routes = []
for i in enumerate(distance):
    routes_polyline = df_strava['map'][i[0]]['summary_polyline']
    routes.append(polyline.decode(routes_polyline, 5))

lats = []
lons = []
for i in enumerate(distance):   
    lats.append([x[0] for x in routes[i[0]] if x != []])
    lons.append([x[1] for x in routes[i[0]] if x != []])

lats = np.array(np.hstack(lats))
lons = np.array(np.hstack(lons))

fig = go.Figure()

fig.add_trace(go.Scattergeo(mode = "markers",lon = lons[::50],lat = lats[::50]))
fig.update_layout(  geo = dict(
                    showland = True,
                    showcountries = True,
                    showocean = True,
                    countrywidth = 0.5,
                    #landcolor = 'rgb(230, 145, 56)',
                    lakecolor = 'rgb(0, 255, 255)',
                    oceancolor = 'rgb(0, 255, 255)',
                    projection = dict(
                        type = 'orthographic',
                    )#,
                    #lonaxis = dict(
                    #    showgrid = True,
                    #    gridcolor = 'rgb(102, 102, 102)',
                    #    gridwidth = 0.5
                    #),
                    #lataxis = dict(
                    #    showgrid = True,
                    #    gridcolor = 'rgb(102, 102, 102)',
                    #    gridwidth = 0.5
                    #)
                )
)
fig.show()
"""
Defines the endpoints available (i.e. the valid paths that users can make requests to),
and their responses.
"""

from . import app
from flask import render_template, request, redirect

import strava_api as api
from . import units


@app.route('/')
def home():
    refresh = request.cookies.get('refresh-token')
    if not refresh:
        # The user hasn't authorized
        return render_template('home/index.html', title='Home', connect_url=api.connect_url, auth=False)
    tokens = api.OAuthTokens.from_refresh(refresh)
    client = api.Client(tokens)

    res = render_template(
        'profile/index.html',
        title='Home',
        connect_url=api.connect_url,
        auth=True,
        # Tell the template how to format distances and elevations
        format_distance=lambda x: units.format_distance(x, client.use_metric),
        format_elevation=lambda x: units.format_elevation(x, client.use_metric),
        format_time=units.format_time,
        # Athlete info
        athlete=client.athlete,
        stats=client.activity_stats,
    )
    print(f"Responded to '{request.path}' with {client.api_calls} API calls")
    return res


@app.route('/about')
def about():
    refresh = request.cookies.get('refresh-token')
    return render_template('about/index.html', title='About', connect_url=api.connect_url, auth=bool(refresh))

@app.route('/co2')
def CO2():
    refresh = request.cookies.get('refresh-token')
    return render_template('co2/index.html', title='CO2', connect_url=api.connect_url, auth=bool(refresh))


@app.route('/authorize')
def authorize():
    # We have an authorization request from Strava
    error = request.args.get('error')
    if error:
        return error

    # Get the access and refresh tokens
    code = request.args.get('code')
    tokens = api.OAuthTokens.from_code(code)

    # Set the refresh token as a cookie on the client
    res = redirect('/')
    res.set_cookie('refresh-token', tokens.refresh, httponly=True, max_age=2592000)

    return res


@app.route('/deauthorize')
def deauthorize():
    # The user wants to log out
    refresh = request.cookies.get('refresh-token')
    if not refresh:
        # The user hasn't authorized
        return render_template('home/index.html', title='Home', connect_url=api.connect_url)

    tokens = api.OAuthTokens.from_refresh(refresh)
    tokens.deauthorize()
    res = redirect('/')
    res.delete_cookie('refresh-token')
    return res

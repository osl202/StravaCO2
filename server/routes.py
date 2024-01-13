"""
Defines the endpoints available (i.e. the valid paths that users can make requests to),
and their responses.
"""

from . import app
from flask import Response, render_template, request, redirect

import strava_api as api
from . import units


@app.route('/')
def home():
    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client:
        # The user hasn't authorized, delete stored token (if exists) and render home
        res = Response(render_template('home/index.html', title='Home', connect_url=api.connect_url, auth=False))
        res.delete_cookie('refresh-token')
        return res

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


@app.route('/stats/activity-times')
def activity_times():
    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if not client: return Response([])
    times = [a.start_date_local.isoformat() for a in client.activities]
    return times


@app.route('/about')
def about():
    refresh = request.cookies.get('refresh-token')
    return render_template('about/index.html', title='About', connect_url=api.connect_url, auth=bool(refresh))


@app.route('/authorize')
def authorize():
    # We have an authorization request from Strava
    error = request.args.get('error')
    if error:
        return error

    client = api.Client.from_code(request.args.get('code'))
    if not client:
        return "Failed to authenticate"

    # Set the refresh token as a cookie on the client
    res = redirect('/')
    res.set_cookie('refresh-token', client.tokens.refresh, httponly=True, max_age=2592000)

    return res


@app.route('/deauthorize')
def deauthorize():
    # The user wants to log out
    client = api.Client.from_refresh(request.cookies.get('refresh-token'))
    if client: client.deauthorize()
    res = redirect('/')
    res.delete_cookie('refresh-token')
    return res

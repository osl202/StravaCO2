from . import app
from flask import render_template, request, Response, redirect
import requests

from . import oauth
from . import api

@app.route('/')
def home():
    refresh = request.cookies.get('refresh-token')
    if not refresh:
        # The user hasn't authorized
        return render_template('home/index.html', title='StravaC02', connect_url=oauth.connect_url, auth=False)

    tokens = oauth.OAuthTokens.from_refresh(refresh)
    res = api.athlete(tokens.access)
    print(str(res))
    return render_template('profile/index.html', title='StravaC02', connect_url=oauth.connect_url, auth=True, **res)

@app.route('/about')
def about():
    refresh = request.cookies.get('refresh-token')
    return render_template('about/index.html', title='StravaC02', connect_url=oauth.connect_url, auth=bool(refresh))

@app.route('/authorize')
def authorize():
    # We have an authorization request from Strava

    error = request.args.get('error')
    if error:
        return error

    # Get the access and refresh tokens
    code = request.args.get('code')
    tokens = oauth.OAuthTokens.from_code(code)

    # Set the refresh token as a cookie on the client
    res = redirect('/')
    res.set_cookie('refresh-token', tokens.refresh, httponly=True, max_age=2592000)

    return res

@app.route('/deauthorize')
def deauthorize():
    refresh = request.cookies.get('refresh-token')
    if not refresh:
        # The user hasn't authorized
        return render_template('home/index.html', title='StravaC02', connect_url=oauth.connect_url)

    tokens = oauth.OAuthTokens.from_refresh(refresh)
    tokens.deauthorize()
    res = redirect('/')
    res.delete_cookie('refresh-token')
    return res

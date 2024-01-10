# StravaCO2

## Setup
- Install required packages with `pip install -r requirements.txt`
- Set the `CLIENT_ID` and `CLIENT_SECRET` environment variables to access the Strava API
- Start the server with `flask run` in the root directory, add the option `--debug` to enable hot refresh of file changes

## File structure
- `server/` contains the flask server
	- `__init__.py` creates the flask app
	- `routes.py` defines the endpoints available on the website, and sends the responses
	- `templates/` contains the html templates which are put together by flask before sending as a response
	- `static/` contains files that are served as-is, e.g. images, CSS styles, JavaScript
- `stravaC02.py` is the entry point, run by flask and will start the server
- `.flaskenv` tells flask which python script to run

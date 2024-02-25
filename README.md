# StravaCO2

## Quick setup
- Install required packages with `pip install -r requirements.txt`
- Set the `CLIENT_ID` and `CLIENT_SECRET` environment variables to access the Strava API (look up how to do this in e.g. bash or zsh, whatever shell you are using)
- Start the server with `flask run` in the root directory, add the option `--debug` to enable hot refresh of file changes
- Visit `localhost:5000` in your web browser

## Flask server
Running the server does something like this:
1. Running the command `flask run` in your terminal will find the `.flaskenv` file and run the script defined there.
2. `stravaC02.py` will start the server by importing the `server` module, which runs `server/__init__.py`.
3. `server/routes.py` is imported, which defines the routes (or endpoints) that the user's browser can connect to.
4. When a user sends a request, a route substitutes variables into a flask *template* from the `server/templates` directory, and sends the completed HTML back to the browser.

Routes are just defined as functions with the `@app.route(path)` decorator, and whatever they return is sent as a response back to the user's browser. So, routes can do anything you might write in a python function, including fetching data from the Strava API.

## Strava API
See the [reference](https://developers.strava.com/docs/reference/) for a list of all the endpoints in Strava's API.
You'll need to create an application in your account to use the API, follow the [getting started](https://developers.strava.com/docs/getting-started/) page to see how.

The `strava_api` module defines a `Client` class which you can use to fetch data from the API.
Every API response is a *model*, which are listed on the Strava API reference and implemented as classes in `strava_api/models.py`, each with a list of fields that are returned in the respose.

## Plotting
Plots are created with [plotly](https://plotly.com/python/).
To create a new plot, make a file in `plotting/plots` -- see `plotting/plots/example.py` for an example of how to do this.

The plots can be viewed in your browser at `localhost:5000/plots/<plot name>`.
To add the plot into a flask template, use an `iframe` to embed it, for example:
```
<iframe width="300px" height="300px" frameborder="0" allowtransparency="true" scrolling="no" src="/plots/example"></iframe>
```
will embed the plot called 'example' into the page.

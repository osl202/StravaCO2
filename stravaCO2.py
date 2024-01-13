from server import app as flask_app
from plotting import app as dash_app
dash_app.init_app(flask_app)

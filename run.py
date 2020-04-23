from flaskwebgui import FlaskUI

from app import app

# Feed it the flask app instance
ui = FlaskUI(app, maximized=True)
ui.run()
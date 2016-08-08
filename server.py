import os
from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar.
# Remember to ``source secrets.sh``!
app.secret_key = os.environ['FLASK_SECRET_KEY']

# If you use an undefined variable in Jinja2, it will raise an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("index.html")


if __name__ == "__main__":

    # Set debug = True in order to invoke the DebugToolbarExtension.
    app.debug = True

    # Use the DebugToolbar.
    DebugToolbarExtension(app)

    # Connect to database
    #connect_to_db(app)

    app.run()

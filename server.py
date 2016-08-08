import os

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from road import request_directions

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar.
# Remember to ``source secrets.sh``!
app.secret_key = os.environ['FLASK_SECRET_KEY']

# If you use an undefined variable in Jinja2, it will raise an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Display index."""

    jskey = os.environ['GOOGLE_API_JAVASCRIPT_KEY']

    return render_template("index.html",
                           jskey=jskey)


@app.route('/request', methods=['POST'])
def handle_form():
    """Handles input from user."""

    jskey = os.environ['GOOGLE_API_JAVASCRIPT_KEY']

    # Get the values needed to create a directions request.
    start = request.form.get("start")
    end = request.form.get("end")
    mode = request.form.get("mode")
    departure = request.form.get("departure")

    directions_result = request_directions(start, end, mode, departure)

    print "overall duration", directions_result[0]['legs'][0]['duration_in_traffic']

    return jsonify(directions_result)


if __name__ == "__main__":

    # Set debug = True in order to invoke the DebugToolbarExtension.
    app.debug = True

    # Use the DebugToolbar.
    DebugToolbarExtension(app)

    # Connect to database
    #connect_to_db(app)

    app.run()

import os

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from road import dictify, marker_info, make_coords_time

import math

app = Flask(__name__)


# Remember to ``source secrets.sh``!
# Required to use Flask sessions and the debug toolbar.
app.secret_key = os.environ['FLASK_SECRET_KEY']

# Required to pass JavaScript API key to render_template.
jskey = os.environ['GOOGLE_API_JAVASCRIPT_KEY']

# Set to StrictUndefined so that Jinja will raise an error if you use an
# undefined variable.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Display index page."""

    return render_template("index.html",
                           jskey=jskey)


# I am a POST request so that the long JSON string is not passed as an argument.
@app.route('/request', methods=['POST'])
def handle_form():
    """Handles input from user."""

    # Get values from form.
    start = request.form.get("start")
    end = request.form.get("end")
    mode = request.form.get("mode")
    departure_day = request.form.get("departure-day")
    departure_time = request.form.get("departure-time")
    directions_result = dictify(request.form.get("data"))

    coords_time = make_coords_time(directions_result, departure_time, departure_day)
    markers_infos = marker_info(coords_time)

    # coords, summary, temp, time = marker_info(coords_time[1])

    # result = {"lat": coords[0], "lng": coords[1], "fsummary": summary, "temp": math.floor(temp), "ftime": time}

    # return jsonify(result)

    return redirect("/")


if __name__ == "__main__":

    # Set debug = True in order to invoke the DebugToolbarExtension.
    app.debug = True

    # Use the DebugToolbarExtension.
    DebugToolbarExtension(app)

    # Connect to database.
    #connect_to_db(app)

    # Must specify port for Vagrant.
    # app.run(host="0.0.0.0")

    app.run()

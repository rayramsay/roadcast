import os

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from road import dictify, marker_info, Route

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
@app.route('/request.json', methods=['POST'])
def handle_form():
    """Handles input from user."""

    # Get values from form.
    start = request.form.get("start")
    end = request.form.get("end")
    mode = request.form.get("mode")
    departure_day = request.form.get("departure-day")
    departure_time = request.form.get("departure-time")
    directions_result = dictify(request.form.get("data"))

    # Instantiate route object.
    timed_route = Route(directions_result, departure_time, departure_day)

    # Make list of coordinates and datetimes.
    coords_time = timed_route.make_coords_time()

    print coords_time

    # Get weather info for coords and times.
    # FIXME: Remember to put me back.
    # result = marker_info(coords_time)

    # FIXME: I'm just here so we don't run out of weather calls.
    result = [{'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 77.0, 'fCloudCover': 1, 'fTime': '2:33 PM EDT', 'lat': 39.8465196, 'lng': -82.81250210000002, 'fIcon': u'rain', 'fSummary': u'Drizzle', 'fPrecipProb': 0.47, 'fPrecipIntensity': 0.0179}, {'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 77.0, 'fCloudCover': 1, 'fTime': '2:48 PM EDT', 'lat': 39.94717, 'lng': -82.84570000000001, 'fIcon': u'rain', 'fSummary': u'Drizzle', 'fPrecipProb': 0.43, 'fPrecipIntensity': 0.0112}, {'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 79.0, 'fCloudCover': 0.98, 'fTime': '3:03 PM EDT', 'lat': 40.11462, 'lng': -82.92744, 'fIcon': u'cloudy', 'fSummary': u'Overcast', 'fPrecipProb': 0.26, 'fPrecipIntensity': 0.0065}, {'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 79.0, 'fCloudCover': 0.97, 'fTime': '3:07 PM EDT', 'lat': 40.1262429, 'lng': -82.92908390000002, 'fIcon': u'cloudy', 'fSummary': u'Overcast', 'fPrecipProb': 0.24, 'fPrecipIntensity': 0.0062}]

    print result

    return jsonify(result)


if __name__ == "__main__":

    # Set debug = True in order to invoke the DebugToolbarExtension.
    app.debug = True

    # There's currently a bug in flask 0.11 that prevents template reloading.
    app.jinja_env.auto_reload = True

    # Use the DebugToolbarExtension.
    # DebugToolbarExtension(app)

    # Connect to database.
    #connect_to_db(app)

    # Must specify port for Vagrant.
    # app.run(host="0.0.0.0")

    app.run()

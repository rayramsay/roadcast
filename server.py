import os

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from road import dictify, make_result

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

    #FIXME: Switch me off once you're ready to make API calls.
    result = {'markerInfo': [{'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 75.0, 'fCloudCover': 0.67, 'fTime': '10:13 AM EDT', 'lat': 39.8465196, 'lng': -82.81250210000002, 'fIcon': u'rain', 'fSummary': u'Drizzle', 'fPrecipProb': 42.0, 'fPrecipIntensity': 0.0104}, {'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 76.0, 'fCloudCover': 0.6, 'fTime': '10:28 AM EDT', 'lat': 39.94295, 'lng': -82.84656000000001, 'fIcon': u'rain', 'fSummary': u'Drizzle', 'fPrecipProb': 41.0, 'fPrecipIntensity': 0.01}, {'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 76.0, 'fCloudCover': 0.6, 'fTime': '10:43 AM EDT', 'lat': 40.11462, 'lng': -82.92744, 'fIcon': u'partly-cloudy-day', 'fSummary': u'Mostly Cloudy', 'fPrecipProb': 24.0, 'fPrecipIntensity': 0.0062}, {'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 76.0, 'fCloudCover': 0.6, 'fTime': '10:47 AM EDT', 'lat': 40.1262429, 'lng': -82.92908390000002, 'fIcon': u'partly-cloudy-day', 'fSummary': u'Mostly Cloudy', 'fPrecipProb': 20.0, 'fPrecipIntensity': 0.0055}], 'weatherReport': {'snowProb': 0.0, 'avgTemp': 76.0, 'modalWeather': u'rainy', 'sleetProb': 0.0, 'precipProb': 79.0, 'rainProb': 79.0}}

    #FIXME: Switch me back on once you're ready to make API calls.
    # result = make_result(directions_result, departure_time, departure_day)
    # print result

    return jsonify(result)


if __name__ == "__main__":

    # Set debug = True in order to invoke the DebugToolbarExtension.
    app.debug = True

    # Use the DebugToolbarExtension.
    # DebugToolbarExtension(app)

    # There's currently a bug in flask 0.11 that prevents template reloading.
    app.jinja_env.auto_reload = True

    # Connect to database.
    #connect_to_db(app)

    # Must specify port for Vagrant.
    # app.run(host="0.0.0.0")

    app.run()

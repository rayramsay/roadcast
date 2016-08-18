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
    result = {'markerInfo': [{'fPrecipType': None, 'fStatus': 'OK', 'fTemp': 86.0, 'fCloudCover': 0.56, 'fTime': '11:30 AM CDT', 'lat': 30.5335476, 'lng': -92.0816484, 'fIcon': u'partly-cloudy-day', 'fSummary': u'Partly Cloudy', 'fPrecipProb': 0, 'fPrecipIntensity': 0}, {'fPrecipType': None, 'fStatus': 'OK', 'fTemp': 87.0, 'fCloudCover': 0.72, 'fTime': '12:00 PM CDT', 'lat': 30.55693, 'lng': -91.65060000000001, 'fIcon': u'partly-cloudy-day', 'fSummary': u'Mostly Cloudy', 'fPrecipProb': 0, 'fPrecipIntensity': 0}, {'fPrecipType': None, 'fStatus': 'OK', 'fTemp': 89.0, 'fCloudCover': 0.15, 'fTime': '12:30 PM CDT', 'lat': 30.43981, 'lng': -91.20334000000001, 'fIcon': u'clear-day', 'fSummary': u'Clear', 'fPrecipProb': 0, 'fPrecipIntensity': 0}, {'fPrecipType': None, 'fStatus': 'OK', 'fTemp': 89.0, 'fCloudCover': 0.44, 'fTime': '1:00 PM CDT', 'lat': 30.202220000000004, 'lng': -90.93957, 'fIcon': u'partly-cloudy-day', 'fSummary': u'Partly Cloudy', 'fPrecipProb': 0, 'fPrecipIntensity': 0}, {'fPrecipType': None, 'fStatus': 'OK', 'fTemp': 84.0, 'fCloudCover': 0.39, 'fTime': '1:30 PM CDT', 'lat': 30.007490000000004, 'lng': -90.21399000000001, 'fIcon': u'partly-cloudy-day', 'fSummary': u'Partly Cloudy', 'fPrecipProb': 0, 'fPrecipIntensity': 0}, {'fPrecipType': u'rain', 'fStatus': 'OK', 'fTemp': 87.0, 'fCloudCover': 0.5, 'fTime': '1:45 PM CDT', 'lat': 29.9510555, 'lng': -90.07148239999998, 'fIcon': u'rain', 'fSummary': u'Light Rain', 'fPrecipProb': 100, 'fPrecipIntensity': 0.0197}], 'weatherReport': {'snowProb': 0, 'rainMax': 0.0197, 'avgTemp': 87.0, 'sleetMax': 0, 'snowMax': 0, 'maxIntensity': 0.0197, 'modalWeather': u'cloudy', 'sleetProb': 0, 'precipProb': 100.0, 'rainProb': 100.0}}

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

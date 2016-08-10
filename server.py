import os

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from road import jsonify_result, get_forecast

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


#FIXME: Why am I a post request? I'm not writing to a database. What about using
# AJAX to send a get req?
@app.route('/request', methods=['POST'])
def handle_form():
    """Handles input from user."""

    # Get values needed to create directions request.
    start = request.form.get("start")
    end = request.form.get("end")
    mode = request.form.get("mode")
    departure_day = request.form.get("departure-day")
    departure_time = request.form.get("departure-time")
    directions_result = request.form.get("data")

    directions_result = jsonify_result(directions_result)
    # print directions_result
    print "\n"
    # print "overall duration: " + str(directions_result["routes"][0]["legs"][0]["duration"])
    print "start lat/lng" + str(directions_result["routes"][0]["legs"][0]["start_location"])
    # print "end lat/lng" + str(directions_result["routes"][0]["legs"][0]["end_location"])
    # print "zeroth step" + str(directions_result["routes"][0]["legs"][0]["steps"][0])
    # print "\n"
    # print start
    # print end
    # print mode
    # print departure_day
    # print departure_time

    start_lat = int(directions_result["routes"][0]["legs"][0]["start_location"]["lat"])
    start_lng = int(directions_result["routes"][0]["legs"][0]["start_location"]["lng"])

    forecast = get_forecast(start_lat, start_lng)

    # Check response status.
    print forecast.response.reason == "OK"
    
    # hourly = get_forecast(start_lat, start_lng).hourly()
    # for hour in hourly.data:
    #     print hour.temperature

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

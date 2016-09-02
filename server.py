import os

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, jsonify
# from flask_debugtoolbar import DebugToolbarExtension

from utils import dictify
from road import make_result, make_recommendation
from model import User, connect_to_db, db

import time

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


####################################################
# JSON routes
####################################################

# I am a POST request so that the long JSON string is not passed as an argument.
@app.route('/request.json', methods=['POST'])
def handle_form():
    """Handles input from user."""

    # Get values from form.
    departure_day = request.form.get("departure-day")
    departure_time = request.form.get("departure-time")
    directions_result = dictify(request.form.get("data"))

    # FIXME: Initial weather results are currently mocked.
    time.sleep(1)
    result = {'routeName': None, 'coordsTime': [((37.8715417, -122.27273809999997), '2016-09-07T17:00:00-07:00'), ((37.83921, -122.26437000000001), '2016-09-07T17:15:00-07:00'), ((37.80339, -122.26879000000001), '2016-09-07T17:30:00-07:00'), ((37.8043732, -122.27113939999998), '2016-09-07T17:31:07-07:00')], 'markerInfo': [{'fIcon': u'cloudy', 'fPrecipType': None, 'fSummary': u'Cloudy', 'fStatus': 'OK', 'fTime': '5:00 PM PDT', 'fPrecipProb': 0, 'lat': 37.8715417, 'lng': -122.27273809999997, 'fPrecipIntensity': 0, 'fTemp': 73.0}, {'fIcon': u'rain', 'fPrecipType': u'rain', 'fSummary': u'Rain', 'fStatus': 'OK', 'fTime': '5:15 PM PDT', 'fPrecipProb': 100, 'lat': 37.83921, 'lng': -122.26437000000001, 'fPrecipIntensity': 0.5, 'fTemp': 70.0}, {'fIcon': u'cloudy', 'fPrecipType': None, 'fSummary': u'Cloudy', 'fStatus': 'OK', 'fTime': '5:30 PM PDT', 'fPrecipProb': 0, 'lat': 37.80339, 'lng': -122.26879000000001, 'fPrecipIntensity': 0, 'fTemp': 70.0}, {'fIcon': u'cloudy', 'fPrecipType': None, 'fSummary': u'Cloudy', 'fStatus': 'OK', 'fTime': '5:31 PM PDT', 'fPrecipProb': 0, 'lat': 37.8043732, 'lng': -122.27113939999998, 'fPrecipIntensity': 0, 'fTemp': 70.0}], 'weatherReport': {'snowProb': 0.0, 'rainMax': 0.5, 'avgTemp': 71.0, 'sleetMax': 0, 'snowMax': 0, 'maxIntensity': 0.5, 'modalWeather': u'cloudy', 'sleetProb': 0.0, 'precipProb': 100.0, 'rainProb': 100.0}}

    # result = make_result(directions_result, departure_time, departure_day)

    return jsonify(result)


@app.route('/recommendation.json', methods=['POST'])
def handle_recs():
    """Handles request for recommendation."""

    # Get values from form.
    minutes_before = int(request.form.get("before"))
    minutes_after = int(request.form.get("after"))
    data = dictify(request.form.get("data"))

    # Check that user is logged in.
    user_id = session.get("user_id")

    if user_id:
        # If they're logged in, pass in their preferences.
        user = User.query.filter(User.user_id == user_id).first()

        sensitivity = user.sensitivity

        result = make_recommendation(data, minutes_before, minutes_after, sensitivity)

    else:
        result = make_recommendation(data, minutes_before, minutes_after)

    return jsonify(result)


# The following code is based on my implementation of Hackbright's Ratings
# exercise, which I pair programmed with Jennifer Griffith-Delgado (jgriffith23).

####################################################
# User profile routes
####################################################
@app.route('/settings', methods=['GET'])
def display_settings():
    """Show a user's profile page."""

    # Check that user is logged in.
    user_id = session.get("user_id")

    # If they're not logged in, redirect them to the homepage.
    if not user_id:
        return redirect("/")

    else:
        user = User.query.filter(User.user_id == user_id).first()
        print user

        return render_template("settings.html", user=user)


@app.route('/settings', methods=['POST'])
def update_settings():
    """Update a user's preferences in the database."""

    # Check that user is logged in.
    user_id = session.get("user_id")

    # If they're not logged in, redirect them to the homepage.
    if not user_id:
        return redirect("/")

    else:
        # Get values from form.
        temp_pref = request.form.get("temp-pref")
        rec_sense = request.form.get("rec-sense")

        # Convert these values into those usable by database.
        # Temperature preference is a boolean (T/F) re: Celsius.
        if temp_pref == "cel":
            temp_pref = True
        else:
            temp_pref = False

        # Sensitivity is an integer.
        if rec_sense == "low":
            rec_sense = -1

        elif rec_sense == "high":
            rec_sense = 1

        else:
            rec_sense = 0

        # Fetch and update user's record.
        user = User.query.filter(User.user_id == user_id).first()

        user.celsius = temp_pref
        user.sensitivity = rec_sense

        db.session.commit()

        return redirect("/settings")


####################################################
# Registration routes
####################################################

@app.route('/register', methods=['GET'])
def register_form():
    """Displays the registration form."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def handle_register():
    """Handles input from registration form."""

    email = request.form.get("email")
    password = request.form.get("password")
    fname = request.form.get("first-name")
    lname = request.form.get("last-name")

    # Python's built-in hash function is not cryptographically secure; we're
    # just using it for convenience.
    password = hash(password)

    user = User.query.filter(User.email == email).first()

    if user:
        flash("That email has already been registered.")
        return redirect("/register")
    else:
        # If the user doesn't exist, create one.
        user = User(email=email, password=password, fname=fname, lname=lname)
        db.session.add(user)
        db.session.commit()

        #Code 307 preserves the POST request, including form data.
        return redirect("/login", code=307)


####################################################
# Authentication/Deauthentication routes
####################################################

@app.route('/login', methods=['POST'])
def handle_login():
    """Handles input from login form."""

    email = request.form.get("email")
    password = request.form.get("password")

    # Python's built-in hash function is not cryptographically secure; we're
    # just using it for convenience.

    # We need to convert the hash to unicode because hash() returns an integer
    # but it's stored in the database as a unicode string.

    password = unicode(hash(password))

    user = User.query.filter(User.email == email).first()

    if user:
        if password != user.password:
            return redirect("/")
        else:
            # Add their user_id and first name to session.
            session["user_id"] = user.user_id
            session["fname"] = user.fname

            print "Session:", session

            return redirect("/")

    else:
        return redirect("/")


@app.route('/logout')
def logout():

    if "user_id" in session:
        del session["user_id"]
        del session["fname"]

    print "Session", session

    return redirect("/")

################################################################################

if __name__ == "__main__":

    # Set debug = True in order to invoke the DebugToolbarExtension.
    app.debug = True

    # Use the DebugToolbarExtension.
    # DebugToolbarExtension(app)

    # There's currently a bug in flask 0.11 that prevents template reloading.
    app.jinja_env.auto_reload = True

    # Connect to database.
    connect_to_db(app)

    # Must specify host for Vagrant.
    app.run(host="0.0.0.0")
    # app.run()

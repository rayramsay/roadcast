import os

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from utils import dictify
from road import make_result, make_coords_datetime, get_alt_weather, make_x_weather, modal_route
from model import User, Label, Addr, connect_to_db, db

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

    # print directions_result
    # print departure_day
    # print departure_time

    result = make_result(directions_result, departure_time, departure_day)

    # print result

    return jsonify(result)


@app.route('/recommendation.json', methods=['POST'])
def handle_recs():
    """Handles request for recommendation."""

    # Get values from form.
    minutes_before = int(request.form.get("before"))
    minutes_after = int(request.form.get("after"))
    data = dictify(request.form.get("data"))

    coords_timestring = data["coordsTime"]
    initial_marker_info = data["markerInfo"]
    initial_weather_report = data["weatherReport"]

    # Make time strings into datetime objects.
    coords_datetime = make_coords_datetime(coords_timestring)

    possibilities = {}
    possibilities["initialRoute"] = {}
    possibilities["initialRoute"]["markerInfo"] = initial_marker_info
    possibilities["initialRoute"]["weatherReport"] = initial_weather_report

    all_possibilities = get_alt_weather(coords_datetime, minutes_before, minutes_after, possibilities)
    print all_possibilities

    best_weather = make_x_weather(all_possibilities, "best")
    print "best", best_weather

    best_mode = modal_route(best_weather)
    print "best mode", best_mode

    result = {}

    if best_mode == "initialRoute":
        result["initialRoute"] = True
    else:
        result["initialRoute"] = False

    result["route"] = all_possibilities[best_mode]
    all_possibilities[best_mode]["time"] = best_mode

    print all_possibilities[best_mode]["time"]

    print result

    return jsonify(result)


# The following code is based on my implementation of Hackbright's Ratings
# exercise, which I pair programmed with Jennifer Griffith-Delgado (jgriffith23).

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
        flash("Account created.")

        #Code 307 preserves the POST request, including form data.
        return redirect("/login", code=307)


####################################################
# Authentication/Deauthentication routes
####################################################

@app.route('/login', methods=['GET'])
def login_form():
    """Displays the login form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def handle_login():
    """Handles input from login/registration form."""

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
            flash("Incorrect password.")
            return redirect("/login")
        else:
            # Add their user_id and first name to session.
            session["user_id"] = user.user_id
            session["fname"] = user.fname

            print "Session:", session

            flash("You've been logged in.")
            return redirect("/")

    else:
        flash("No account with that email exists.")
        return redirect("/login")


@app.route('/logout')
def logout():

    if "user_id" in session:
        del session["user_id"]
        del session["fname"]
        flash("You've been logged out.")
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
    # connect_to_db(app)

    # Must specify host for Vagrant.
    #app.run(host="0.0.0.0")
    app.run()

import os

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from road import dictify, make_result
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

    result = {'markerInfo': [{'fPrecipType': None, 'fStatus': 'OK', 'fTemp': 69.0, 'fCloudCover': 0.08, 'fTime': '2:30 PM PDT', 'lat': 37.8716404, 'lng': -122.27275600000002, 'fIcon': u'clear-day', 'fSummary': u'Clear', 'fPrecipProb': 0, 'fPrecipIntensity': 0}, {'fPrecipType': None, 'fStatus': 'OK', 'fTemp': 67.0, 'fCloudCover': 0.12, 'fTime': '2:45 PM PDT', 'lat': 37.811040000000006, 'lng': -122.36414, 'fIcon': u'clear-day', 'fSummary': u'Clear', 'fPrecipProb': 0, 'fPrecipIntensity': 0}, {'fPrecipType': None, 'fStatus': 'OK', 'fTemp': 65.0, 'fCloudCover': 0.13, 'fTime': '2:54 PM PDT', 'lat': 37.7749901, 'lng': -122.41949260000001, 'fIcon': u'clear-day', 'fSummary': u'Clear', 'fPrecipProb': 0, 'fPrecipIntensity': 0}], 'weatherReport': {'snowProb': 0.0, 'rainMax': 0, 'avgTemp': 67.0, 'sleetMax': 0, 'snowMax': 0, 'maxIntensity': 0, 'modalWeather': u'clear', 'sleetProb': 0.0, 'precipProb': 0.0, 'rainProb': 0.0}}

    #FIXME: Switch me back on once you're ready to make API calls.
    # result = make_result(directions_result, departure_time, departure_day)
    # print result

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
    # just using it for convenience. (We need to convert it to unicode because
    # hash returns an integer but unicode is its type out of the database.)
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

            print "Session:", session, "\n"

            flash("You've been logged in.")
            return redirect("/")

    else:
        flash("No account with that email exists.")
        return redirect("/login")


if __name__ == "__main__":

    # Set debug = True in order to invoke the DebugToolbarExtension.
    app.debug = True

    # Use the DebugToolbarExtension.
    # DebugToolbarExtension(app)

    # There's currently a bug in flask 0.11 that prevents template reloading.
    app.jinja_env.auto_reload = True

    # Connect to database.
    connect_to_db(app)
    print "Connected to DB."

    # Must specify host for Vagrant.
    app.run(host="0.0.0.0")

import os
import googlemaps
import pendulum
import json

# Remember to ``source secrets.sh``!

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])


def format_time(start, departure_day, departure_time):
    pass

    #FIXME: intelligently handle departure time based on starting location.

    geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')


    # You can specify the time as an integer in seconds since midnight,
    # January 1, 1970 UTC. Alternatively, you can specify a value of now,
    # which sets the departure time to the current time (correct to the
    # nearest second).


# Although I cannot pass departure time to the Maps JavaScript API, departure
# time is an acceptable parameter for the Web Services Directions API.


def jsonify_result(directions_result):
    """Given a directions_result as a string, make it into a dictionary."""
    return json.loads(directions_result)

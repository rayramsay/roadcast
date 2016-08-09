import os
import googlemaps
import pendulum

# Remember to ``source secrets.sh``!

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])


def format_time(start, departure_day, departure_time):
    pass

    #FIXME: intelligently handle departure time based on starting location.
    #FIXME: separate function for handling time?

    departure = pendulum.now()

    # You can specify the time as an integer in seconds since midnight,
    # January 1, 1970 UTC. Alternatively, you can specify a value of now,
    # which sets the departure time to the current time (correct to the
    # nearest second).


# Although I cannot pass departure time to the Maps JavaScript API, departure
# time is an acceptable parameter for the Web Services Directions API.

def request_directions(start, end, mode, departure_day, departure_time):
    """Given starting point, destination, mode of transportation, and day and
    time of departure, requests directions from Google Maps."""

    # Python wrapper requires this to be in lower case.
    mode = mode.lower()

    departure_time = format_time(start, departure_day, departure_time)

    if mode == "driving":
        directions_result = gmaps.directions(origin=start,
                                             destination=end,
                                             mode=mode,
                                             departure_time=departure_time)

    # Only driving or transit mode accepts departure time.
    else:
        directions_result = gmaps.directions(origin=start,
                                             destination=end,
                                             mode=mode)

    return directions_result

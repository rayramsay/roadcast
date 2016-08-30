import os
import math
import googlemaps
import pendulum
from collections import Counter
from routes import prep_directions, Route
from weather import make_marker_info, make_weather_report
from utils import normalize
import logging

# Suppress requests' warnings while on Vagrant.
logging.captureWarnings(True)

############# GLOBALS ##############

# Remember to ``source secrets.sh``!

GMAPS = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])

####################################


def make_result(directions_result, departure_time, departure_day):
    """Builds the initial result dictionary for jsonification."""

    result = {}

    # Prepare the directions result.
    directions_prepped = prep_directions(directions_result)

    # Instantiate route object.
    timed_route = Route(directions_prepped, departure_time, departure_day)

    # Make list of coordinates and datetimes.
    coords_time = timed_route.make_coords_time()

    # Get weather info for coords and times.
    marker_info = make_marker_info(coords_time)

    # Make weather report for trip.
    weather_report = make_weather_report(marker_info)

    # Convert datetimes to strings.
    formatted_ct = format_coords_time(coords_time)

    result["markerInfo"] = marker_info
    result["weatherReport"] = weather_report
    result["coordsTime"] = formatted_ct
    result["routeName"] = None

    return result


def format_coords_time(coords_time):
    """Change datetimes into strings before sending to frontend."""

    formatted_ct = []

    for ct in coords_time:
        coords, time = ct
        time = time.to_iso8601_string()
        formatted_ct.append((coords, time))

    return formatted_ct


def make_recommendation(data, minutes_before, minutes_after):
    """Build recommendation dictionary for jsonification."""

    result = {}

    coords_timestring = data["coordsTime"]
    initial_marker_info = data["markerInfo"]
    initial_weather_report = data["weatherReport"]

    # Make time strings into datetime objects.
    coords_datetime = make_coords_datetime(coords_timestring)

    # Put initialRoute into possibilities dictionary.
    possibilities = {"initialRoute": {"markerInfo": initial_marker_info, "weatherReport": initial_weather_report}}

    # Add alternate routes into possibilities dictionary.
    possibilities = get_alt_weather(coords_datetime, minutes_before, minutes_after, possibilities)

    best_weather = make_x_weather(possibilities, "best")

    best_route = modal_route(best_weather)

    # Set routeName.
    result["routeName"] = best_route

    if result["routeName"] != "initialRoute":

        # Calculate differences between initialRoute and best route.
        differences = {}

        weather_attributes = ["precipProb", "maxIntensity"]

        for w_a in weather_attributes:
            differences[w_a] = make_difference(possibilities, best_route, w_a)

        if differences["precipProb"] < 5 and differences["maxIntensity"] < 0.02:

            # That's not a big enough difference, don't tell the user.
            result["routeName"] = "initialRoute"

        else:

            # If route is a sufficient improvement, add its information.
            result["markerInfo"] = possibilities[best_route]["markerInfo"]
            result["weatherReport"] = possibilities[best_route]["weatherReport"]
            result["differences"] = differences

    return result


def make_coords_datetime(coords_timestring):
    """Given a coords_time array with times as strings, recreates as a list of
    (coords, datetimes) lists."""

    coords_datetime = []

    start_lat, start_lng = coords_timestring[0][0]
    start_coords = (start_lat, start_lng)

    timezone_result = GMAPS.timezone(start_coords)
    timezone_id = timezone_result["timeZoneId"]

    for ct in coords_timestring:
        coords, time = ct
        time = time[:-6]

        coords = tuple(coords)
        datetime = pendulum.parse(time, timezone_id)

        coords_datetime.append([coords, datetime])

    return coords_datetime


def shift_time(coords_datetime, direction, minutes):
    """Shifts datetime in specified direction by number of minutes."""

    shifted = []

    for ct in coords_datetime:
        coords, time = ct
        if direction == "forward" or direction == "forwards":
            time = time.add(minutes=minutes)
        elif direction == "backward" or direction == "backwards":
            time = time.subtract(minutes=minutes)
        else:
            raise ValueError("Direction can only be forward or backward.")
        shifted.append((coords, time))

    return shifted


def get_alt_weather(coords_datetime, minutes_before, minutes_after, possibilities):

    interval = 30

    if minutes_before > 0:
        # Divide minutes_before into 30 minute increments.
        num = minutes_before / interval

        count = 1
        while count <= num:

            minutes = interval * count  # 30 * 1 => 30 * 2
            key = "before"+str(minutes)

            new_ct = shift_time(coords_datetime, "backward", minutes)

            # Get weather at new coords, datetime.
            marker_info = make_marker_info(new_ct)

            # Make weather report for trip.
            weather_report = make_weather_report(marker_info)

            possibilities[key] = {}
            possibilities[key]["markerInfo"] = marker_info
            possibilities[key]["weatherReport"] = weather_report

            count += 1

    if minutes_after > 0:
        # Divide minutes_before into 30 minute increments.
        num = minutes_after / interval

        count = 1
        while count <= num:

            minutes = interval * count  # 30 * 1 => 30 * 2
            key = "after"+str(minutes)

            new_ct = shift_time(coords_datetime, "forward", minutes)

            # Get weather at new coords, datetime.
            marker_info = make_marker_info(new_ct)

            # Make weather report for trip.
            weather_report = make_weather_report(marker_info)

            possibilities[key] = {}
            possibilities[key]["markerInfo"] = marker_info
            possibilities[key]["weatherReport"] = weather_report

            count += 1

    return possibilities


def make_x_weather(possibilities, quality):
    """Biased toward initialRoute."""

    weather = {}
    weather_attributes = ["precipProb", "maxIntensity"]

    if quality == "worst":
        for attribute in weather_attributes:
            worst_attribute = 0

            for key in sorted(possibilities.keys(), reverse=True):
                if possibilities[key]["weatherReport"][attribute] > worst_attribute:
                    worst_attribute = possibilities[key]["weatherReport"][attribute]
                    weather[attribute] = key

    elif quality == "best":
        for attribute in weather_attributes:
            best_attribute = 100

            for key in sorted(possibilities.keys(), reverse=True):
                if possibilities[key]["weatherReport"][attribute] < best_attribute:
                    best_attribute = possibilities[key]["weatherReport"][attribute]
                    weather[attribute] = key

    else:
        raise ValueError("Quality can only be best or worst.")

    return weather


def make_difference(possibilities, best_route, weather_attr):

    difference = possibilities["initialRoute"]["weatherReport"][weather_attr] - possibilities[best_route]["weatherReport"][weather_attr]

    return difference


def modal_route(x_weather):
    """Given a dictionary of best/worst weather, return most common route.

    In the event of multi-modality, biased toward initialRoute."""

    cnt = Counter()

    for value in x_weather.itervalues():
        cnt[value] += 1

    ordered_by_count = cnt.most_common()

    if cnt['initialRoute'] == ordered_by_count[0][0]:
        mode = "initialRoute"

    else:
        mode = ordered_by_count[0][0]

    return mode

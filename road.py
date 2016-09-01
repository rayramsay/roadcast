from routes import prep_directions, Route
from weather import make_marker_info, make_weather_report
from comparison import make_coords_datetime, get_alt_weather, make_x_weather, modal_route, make_per_change, make_abs_diff
import logging

# Suppress requests' warnings while on Vagrant.
logging.captureWarnings(True)

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


def make_recommendation(data, minutes_before, minutes_after, sensitivity=None):
    """Build recommendation dictionary for jsonification."""

    result = {}

    weather_attributes = ["precipProb", "maxIntensity"]

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

        # Calculate percentage changes, absolute differences, and thresholds between initialRoute and best route.
        changes = {}
        absolutes = {}
        thresholds = {}

        for w_a in weather_attributes:
            changes[w_a] = make_per_change(possibilities, best_route, w_a)
            absolutes[w_a] = make_abs_diff(possibilities, best_route, w_a)
            thresholds[w_a] = changes[w_a] * absolutes[w_a]

        print "changes", changes
        print "absolutes", absolutes
        print "thresholds", thresholds

        if sensitivity:
            if sensitivity < 0:  # Low sensitivity.
                preferences = {"precipProb": -1000}
            elif sensitivity > 0:  # High sensitivity.
                preferences = {"precipProb": -100}
            else:  # Medium/default sensitivity.
                preferences = {"precipProb": -500}

        else:
            # Set defaults.
            preferences = {"precipProb": -500}

        if thresholds["precipProb"] > preferences["precipProb"]:
            # That's not a big enough change, don't tell the user.
            result["routeName"] = "initialRoute"

        else:
            # If route is a sufficient improvement, add its information.
            result["markerInfo"] = possibilities[best_route]["markerInfo"]
            result["weatherReport"] = possibilities[best_route]["weatherReport"]
            result["changes"] = changes
            # result["absolutes"] = absolutes

    return result

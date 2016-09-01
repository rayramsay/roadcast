import os
import googlemaps
import pendulum
from collections import Counter
from weather import make_marker_info, make_weather_report

############# GLOBALS ##############

# Remember to ``source secrets.sh``!

GMAPS = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])

####################################


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
    """Biased toward initialRoute, then toward times closer to initialRoute."""

    weather = {}
    weather_attributes = ["precipProb", "maxIntensity"]

    if quality == "best":
        for attribute in weather_attributes:
            best_attribute = 100

            for key in ['initialRoute'] + sorted(possibilities.keys(), key=lambda i: i[-2:])[:-1]:
                if possibilities[key]["weatherReport"][attribute] < best_attribute:
                    best_attribute = possibilities[key]["weatherReport"][attribute]
                    weather[attribute] = key

    elif quality == "worst":
        for attribute in weather_attributes:
            worst_attribute = 0

            for key in ['initialRoute'] + sorted(possibilities.keys(), key=lambda i: i[-2:])[:-1]:
                if possibilities[key]["weatherReport"][attribute] > worst_attribute:
                    worst_attribute = possibilities[key]["weatherReport"][attribute]
                    weather[attribute] = key

    else:
        raise ValueError("Quality can only be best or worst.")

    return weather


def make_per_change(possibilities, best_route, weather_attr):
    """Calculate percentage change of weather attribute between initialRoute and recommended route."""

    old_value = possibilities["initialRoute"]["weatherReport"][weather_attr]
    new_value = possibilities[best_route]["weatherReport"][weather_attr]

    print "old", old_value
    print "new", new_value

    # Avoiding dividing by zero.
    if old_value == 0 and weather_attr == "precipProb":
        per_change = 10000
    elif old_value == 0 and weather_attr == "maxIntensity":
        per_change = 50000
    else:
        per_change = ((new_value - old_value)/old_value) * 100

    return per_change


def make_abs_diff(possibilities, best_route, weather_attr):
    """Calculate absolute difference in percentage points of weather attribute between initialRoute and recommended route."""

    old_value = possibilities["initialRoute"]["weatherReport"][weather_attr]
    new_value = possibilities[best_route]["weatherReport"][weather_attr]

    absolute = old_value - new_value

    return absolute


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

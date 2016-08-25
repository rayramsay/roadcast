import os
import googlemaps
import pendulum
from routes import prep_directions, Route
from weather import make_marker_info, make_weather_report

############# GLOBALS ##############

# Remember to ``source secrets.sh``!

GMAPS = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])

####################################


def make_result(directions_result, departure_time, departure_day):
    """Builds the dictionary for jsonification."""

    result = {}

    # Prepare the directions result.
    directions_prepped = prep_directions(directions_result)

    # Instantiate route object.
    timed_route = Route(directions_prepped, departure_time, departure_day)

    # print timed_route

    # Make list of coordinates and datetimes.
    coords_time = timed_route.make_coords_time()

    # print coords_time

    # Get weather info for coords and times.
    marker_info = make_marker_info(coords_time)

    # print marker_info

    # Make weather report for trip.
    weather_report = make_weather_report(marker_info)

    # print weather_report

    # Convert datetimes to strings.
    formatted_ct = format_coords_time(coords_time)

    # print formatted_ct

    result["markerInfo"] = marker_info
    result["weatherReport"] = weather_report
    result["coordsTime"] = formatted_ct

    # print result

    return result


def format_coords_time(coords_time):
    """Change datetimes into strings before sending to frontend."""

    formatted_ct = []

    for ct in coords_time:
        coords, time = ct
        time = time.to_iso8601_string()
        formatted_ct.append((coords, time))

    return formatted_ct


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
        else:
            time = time.subtract(minutes=minutes)
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


def make_score(possibilities):
    """Calculate ``badness`` of weather score."""

    pass


####################################

#FIXME: Does this still get used anywhere?
# def get_lat_lng(loc_string):
    """Given location as a human-readable string, return its latitude and
    longitude as a tuple of floats."""

    geocode_result = GMAPS.geocode(loc_string)
    lat = float(geocode_result[0]["geometry"]["location"]["lat"])
    lng = float(geocode_result[0]["geometry"]["location"]["lng"])
    tup = (lat, lng)

    return tup

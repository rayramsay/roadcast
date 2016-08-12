import os
import googlemaps
import forecastio
import pendulum
import datetime
import json

# Remember to ``source secrets.sh``!

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])
fio_key = os.environ['FORECAST_API_KEY']

#FIXME: I'm just for testing.
oakcords = (37.8043637, -122.2711137)


def get_lat_lng(loc_string):
    """Given location as a human-readable string, return its latitude and
    longitude as a tuple of floats."""

    geocode_result = gmaps.geocode(loc_string)
    lat = float(geocode_result[0]["geometry"]["location"]["lat"])
    lng = float(geocode_result[0]["geometry"]["location"]["lng"])
    tup = (lat, lng)

    return tup


def format_time(coords, time):
    """Given a lat/lng tuple and time as a string, return a timezone-aware
    Pendulum datetime object."""

    timezone_result = gmaps.timezone(coords)
    timezone_id = timezone_result["timeZoneId"]

    # Note that the time's date will be the current date in that timezone.
    time = pendulum.parse(time, timezone_id)

    return time


def dictify(directions_result):
    """Given a directions_result as a string, make it into a dictionary."""
    return json.loads(directions_result)


def get_forecast(coords, time):
    """Given lat/lng tuple and Pendulum datetime object, return forecast."""

    lat = coords[0]
    lng = coords[1]

    # Convert to ISO 8601 string.
    time = time.to_iso8601_string()

    url = 'https://api.forecast.io/forecast/%s/%s,%s,%s' \
        % (fio_key, lat, lng, time)

    return forecastio.manual(url)


def convert_time(time):
    """Given a datetime object from Forecast.io, (e.g., forecast.time), convert
    to a timezone-aware Pendulum datetime object."""

    return pendulum.instance(time)


def make_coords_time(directions_result, departure_time, departure_day):
    """Given a directions_result dictionary, departure time as a string, and
    departure day, make a list of tuples containing coords and datetimes."""

    coords_time = []
    steps = directions_result["routes"][0]["legs"][0]["steps"]

    # Make coords for the starting location of the first step.
    lat = steps[0]["start_location"]["lat"]
    lng = steps[0]["start_location"]["lng"]
    start_location = (lat, lng)

    start_time = format_time(start_location, departure_time)
    if departure_day == "tomorrow":
        start_time = start_time.add(days=1)

    # Add starting location coordinates and formatted departure time to list of
    # (coord, datetime) tuples.
    coords_time.append((start_location, start_time))

    # Get trip duration in seconds.
    overall_duration = int(directions_result["routes"][0]["legs"][0]["duration"]["value"])
    current_duration = 0

    # If trip is shorter than 15 minutes, pick middle coord.
    # if overall_duration < 900:
    for step in steps:
        step_duration = int(step["duration"]["value"])

        # If taking this step would put you over the halfway point:
        if (current_duration + step_duration) > overall_duration/2:

            # Pick middle (or if len(paths) is even, one past) path coord.
            index = len(step["path"])/2

            # Make coords.
            lat = step["path"][index]["lat"]
            lng = step["path"][index]["lng"]
            coords = (lat, lng)

            # Divide step's duration by number of coords in its path.
            seconds_per_interval = step_duration / len(step["path"])-1

            # Add seconds up to selected coord.
            current_duration += (seconds_per_interval * index)
            time = start_time.add(seconds=current_duration)

            # Append coords, time to list.
            coords_time.append((coords, time))

            # Add time for rest of step. FIXME
            current_duration += seconds_per_interval * (len(step["path"]) - index)
            break
        else:
            current_duration += step_duration

    # Make coords for the ending location of the last step.
    lat = steps[-1]["end_location"]["lat"]
    lng = steps[-1]["end_location"]["lng"]
    end_location = (lat, lng)

    time = start_time.add(seconds=overall_duration)

    coords_time.append((end_location, time))

    return coords_time

    # If trip is longer than 15 minutes, start making fifteen minute buckets.
    if overall_duration > 900:
        for step in steps:
            step_duration = int(step["duration"])
            # if (current_duration += step_duration) > 900:




def marker_info(coord_time):
    """Given a coord, time tuple, return the weather forecast at that coord and time."""

    coords = coord_time[0]

    time = coord_time[1]

    forecast = get_forecast(coords, time).currently()

    time = time.to_iso8601_string()

    summary = forecast.summary
    icon = forecast.icon

    temp = forecast.temperature
    precipProb = forecast.precipProbability

    if precipProb > 0:
        precipType = forecast.precipType
        precipIntensity = forecast.precipIntensity

    return [coords, summary, temp, time]

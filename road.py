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


def slice_step(step, fraction_needed):
    """Cuts off part of step."""
    index = int(fraction_needed * len(step["path"]))  # Indices must be ints.
    sliced_step = {
        u'duration': {u'value': int(step["duration"]["value"]) * (1 - fraction_needed)},
        u'path': step["path"][index + 1:],
        u'end_location': step["end_location"]}
    return sliced_step


def fill_buckets(step, time_in_bucket, size_of_bucket, abs_time, coords_time):
    """Given a step, fills buckets to get middle coords."""
    # FIXME: How is abs_time getting messed up?
    # FIXME: Maybe have a separate time_elapsed variable like in the middle picker?
    step_duration = int(step["duration"]["value"])
    if (time_in_bucket + step_duration) < size_of_bucket:
        print "I fit in the bucket"
        time_in_bucket += step_duration
        abs_time = abs_time.add(seconds=step_duration)
        print abs_time
        return
    elif (time_in_bucket + step_duration) == size_of_bucket:
        print "I exactly fill the bucket"
        lat = step["end_location"]["lat"]
        lng = step["end_location"]["lng"]
        end_location = (lat, lng)
        abs_time.add(seconds=step_duration)
        print abs_time
        coords_time.append((end_location, abs_time))
        time_in_bucket = 0  # Empty the bucket.
        return
    else:
        print "I'm too big!"
        needed_time = size_of_bucket - time_in_bucket
        fraction_needed = needed_time / float(step_duration)  # Don't floor this fraction.
        index = int(fraction_needed * len(step["path"]))  # Indices must be ints.
        lat = step["path"][index]["lat"]
        lng = step["path"][index]["lng"]
        location = (lat, lng)
        abs_time = abs_time.add(seconds=needed_time)
        print abs_time
        coords_time.append((location, abs_time))
        sliced_step = slice_step(step, fraction_needed)
        fill_buckets(sliced_step, time_in_bucket, size_of_bucket, abs_time, coords_time)


def make_coords_time(directions_result, departure_time, departure_day):
    """Given a directions_result dictionary, departure time as a string, and
    departure day, make a list of tuples containing coords and datetimes."""

    coords_time = []
    # FIXME: Bucket small for testing; reset to 900.
    size_of_bucket = 120  # Get coords every fifteen minutes (900 seconds).
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

    # If trip is shorter than 15 minutes, just pick middle coord.
    if overall_duration < size_of_bucket:
        time_elapsed = 0
        for step in steps:
            step_duration = int(step["duration"]["value"])

            # If taking this step would put you over the halfway point:
            if (time_elapsed + step_duration) > overall_duration/2:

                # Pick middle (or if len(paths) is even, one past) path coord.
                index = len(step["path"])/2

                # Make coords.
                lat = step["path"][index]["lat"]
                lng = step["path"][index]["lng"]
                coords = (lat, lng)

                # Divide step's duration by intervals in path.
                seconds_per_interval = step_duration / len(step["path"])-1

                # Add seconds up to selected coord.
                time_elapsed += (seconds_per_interval * index)
                time = start_time.add(seconds=time_elapsed)

                # Append coords, time to list.
                coords_time.append((coords, time))

                # Add time for rest of step.
                time_elapsed += seconds_per_interval * ((len(step["path"])-1 - index))
                break
            else:
                time_elapsed += step_duration

    else:
        time_in_bucket = 0
        abs_time = start_time
        for step in steps:
            print "I'm starting on a step!"
            print abs_time
            fill_buckets(step, time_in_bucket, size_of_bucket, abs_time, coords_time)

    # Make coords for the ending location of the last step.
    lat = steps[-1]["end_location"]["lat"]
    lng = steps[-1]["end_location"]["lng"]
    end_location = (lat, lng)

    end_time = start_time.add(seconds=overall_duration)
    coords_time.append((end_location, end_time))

    return coords_time


def marker_info(coords_time):
    """Given a list of (coords, time) tuples, return the weather forecasts at those coords and times."""

    results = {}
    counter = 0

    for tup in coords_time:
        coords = tup[0]
        time = tup[1]
        counter += 1
        forecast = get_forecast(coords, time).currently()
        print forecast.time, forecast.summary, forecast.icon
        # print forecast.precipIntensity, forecast.precipProb
        # if forecast.precipType:
            # print forecast.precipType
        print forecast.temperature

    # FIXME: Figure out what you want from the forecast. Also format time as a string?

    #     summary = forecast.summary
    #     icon = forecast.icon
    #     temp = forecast.temperature
    #     precipProb = forecast.precipProbability

    #     if precipProb > 0:
    #         precipType = forecast.precipType
    #         precipIntensity = forecast.precipIntensity

    #     results[counter] = {"summary": summary, "icon": icon}

    # return results

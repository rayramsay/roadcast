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


def marker_info(directions_result, departure_time, departure_day):
    """Given a directions_result dictionary, departure time as a string, and
    departure day, return the weather forecast at the first step's starting
    location."""

    lat = directions_result["routes"][0]["legs"][0]["steps"][0]["start_location"]["lat"]
    lng = directions_result["routes"][0]["legs"][0]["steps"][0]["start_location"]["lng"]
    coords = (lat, lng)

    time = format_time(coords, departure_time)

    if departure_day == "tomorrow":
        time = time.add(days=1)

    forecast = get_forecast(coords, time).currently()

    summary = forecast.summary
    icon = forecast.icon

    temp = forecast.temperature
    precipProb = forecast.precipProbability

    if precipProb > 0:
        precipType = forecast.precipType
        precipIntensity = forecast.precipIntensity

    return [coords, summary, temp]

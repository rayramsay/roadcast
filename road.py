import os
import googlemaps
import forecastio
import pendulum
import json

# Remember to ``source secrets.sh``!

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])
fio_key = os.environ['FORECAST_API_KEY']

def format_time(start, departure_day, departure_time):
    """Given a starting location, departure day, and departure time, return a
    timezone-aware datetime object."""

    # FIXME: Break me into separate functions, one to get co-ords and one to
    # create a timezone-aware datetime object.

    geocode_result = gmaps.geocode(start)
    lat = geocode_result[0]["geometry"]["location"]["lat"]
    lng = geocode_result[0]["geometry"]["location"]["lng"]
    tup = (lat, lng)

    timezone_result = gmaps.timezone(tup)
    timezone_id = timezone_result["timeZoneId"]

    departure_time = pendulum.parse(departure_time, timezone_id)
    if departure_day == "tomorrow":
        departure_time = departure_time.add(days=1)

    return departure_time


def jsonify_result(directions_result):
    """Given a directions_result as a string, make it into a dictionary."""
    return json.loads(directions_result)


def get_forecast(lat, lng):
    """Given a lat and lng as integers, return forecast."""

    # FIXME: Add time parameter.

    return forecastio.load_forecast(fio_key, lat, lng)

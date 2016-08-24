import os
#import googlemaps
from routes import prep_directions, Route
from weather import make_marker_info, make_weather_report

############# GLOBALS ##############

# Remember to ``source secrets.sh``!

#GMAPS = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])

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

    print coords_time

    # Get weather info for coords and times.
    marker_info = make_marker_info(coords_time)

    # print marker_info

    # Make weather report for trip.
    weather_report = make_weather_report(marker_info)

    print weather_report

    result["markerInfo"] = marker_info
    result["weatherReport"] = weather_report

    # print result

    return result


def make_score(weather_results):
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

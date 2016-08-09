import os
import googlemaps
import pendulum

# Remember to ``source secrets.sh``!

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])

# Although I cannot pass departure time to the Maps JavaScript API, departure
# time is an acceptable parameter for the Web Services Directions API.

def request_directions(start, end, mode, departure):
    """Given starting point, destination, mode of transportation, and time of
    departure, requests directions from Google Maps."""

    # Python wrapper requires this to be in lower case.
    mode = mode.lower()

    if mode == "driving":

        #FIXME: intelligently handle departure time based on starting location.
        #FIXME: separate function for handling time?

        departure = pendulum.now()

        # You can specify the time as an integer in seconds since midnight,
        # January 1, 1970 UTC. Alternatively, you can specify a value of now,
        # which sets the departure time to the current time (correct to the
        # nearest second).

        directions_result = gmaps.directions(origin=start,
                                             destination=end,
                                             mode=mode,
                                             departure_time=departure)

    # Only driving or transit mode accept departure time.
    else:
        directions_result = gmaps.directions(origin=start,
                                             destination=end,
                                             mode=mode)

    return directions_result

# # print "start address", directions_result[0]['legs'][0]['start_address']
# # print "start location", directions_result[0]['legs'][0]['start_location']
# # print "end address", directions_result[0]['legs'][0]['end_address']
# # print "end location", directions_result[0]['legs'][0]['end_location']
# print "overall duration", directions_result[0]['legs'][0]['duration_in_traffic']

# print "zero index step duration", directions_result[0]['legs'][0]['steps'][0]['duration']
# print "zero index step start location", directions_result[0]['legs'][0]['steps'][0]['start_location']
# print "zero index step end location", directions_result[0]['legs'][0]['steps'][0]['end_location']

# # steps = directions_result[0]['legs'][0]['steps']
# # for step in steps:
# #     print step

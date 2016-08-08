import os
import googlemaps
import pendulum

# Remember to ``source secrets.sh``!

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])


def request_directions(start, end, mode, departure):
    """Given starting point, destination, mode of transportation, and time of
    departure, requests directions from Google Maps."""

    # departure = pendulum.parse(departure)
    # print departure

    #FIXME: actually handle time based on user input rather than doing this:
    departure = pendulum.now()

    directions_result = gmaps.directions(origin=start,
                                         destination=end,
                                         mode=mode,
                                         departure_time=departure)

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

import os
import googlemaps
import pendulum
import datetime

# Remember to ``source secrets.sh``!

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])

# Request directions
now = datetime.datetime.now()
directions_result = gmaps.directions("Oakland, CA",
                                     "San Francisco, CA",
                                     mode="driving",
                                     departure_time=now)

# print "start address", directions_result[0]['legs'][0]['start_address']
# print "start location", directions_result[0]['legs'][0]['start_location']
# print "end address", directions_result[0]['legs'][0]['end_address']
# print "end location", directions_result[0]['legs'][0]['end_location']
print "overall duration", directions_result[0]['legs'][0]['duration_in_traffic']

print "zero index step duration", directions_result[0]['legs'][0]['steps'][0]['duration']
print "zero index step start location", directions_result[0]['legs'][0]['steps'][0]['start_location']
print "zero index step end location", directions_result[0]['legs'][0]['steps'][0]['end_location']

# steps = directions_result[0]['legs'][0]['steps']
# for step in steps:
#     print step

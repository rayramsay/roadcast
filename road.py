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


# def fill_buckets(step, size_of_bucket, time_in_bucket, time_elapsed, start_time, coords_time):
#     """Given a step, fills buckets to get middle coords."""

#     step_duration = int(step["duration"]["value"])

#     if (time_in_bucket + step_duration) < size_of_bucket:
#         print "I fit in the bucket!"

#         time_in_bucket = time_in_bucket + step_duration
#         time_elapsed = time_elapsed + step_duration

#         print "step duration", step_duration
#         print "time in bucket", time_in_bucket
#         print "time elapsed", time_elapsed

#         return 

#     elif (time_in_bucket + step_duration) == size_of_bucket:
#         print "I exactly fill the bucket!"

#         time_in_bucket += step_duration
#         time_elapsed += step_duration

#         lat = step["end_location"]["lat"]
#         lng = step["end_location"]["lng"]
#         end_location = (lat, lng)

#         time = start_time.add(seconds=time_elapsed)
#         coords_time.append((end_location, time))

#         print "step duration", step_duration
#         print "time in bucket", time_in_bucket
#         print "time elapsed", time_elapsed

#         time_in_bucket = 0  # Empty the bucket.

#         return

#     else:
#         print "I'm too big!"

#         needed_time = size_of_bucket - time_in_bucket
#         time_elapsed += needed_time

#         fraction_needed = needed_time / float(step_duration)  # Don't floor this fraction.

#         index = int(fraction_needed * len(step["path"]))  # Indices must be ints.
#         lat = step["path"][index]["lat"]
#         lng = step["path"][index]["lng"]
#         location = (lat, lng)

#         time = start_time.add(seconds=time_elapsed)
#         coords_time.append((location, time))

#         print "step duration", step_duration
#         print "time in bucket", time_in_bucket
#         print "time elapsed", time_elapsed

#         time_in_bucket = 0  # Empty the bucket.

#         sliced_step = slice_step(step, fraction_needed)
#         fill_buckets(sliced_step, size_of_bucket, time_in_bucket, time_elapsed, start_time, coords_time)


# def make_coords_time(directions_result, departure_time, departure_day):
#     """Given a directions_result dictionary, departure time as a string, and
#     departure day, make a list of tuples containing coords and datetimes."""

#     coords_time = []
#     # FIXME: Bucket small for testing; reset to 900.
#     size_of_bucket = 120  # Get coords every fifteen minutes (900 seconds).
#     steps = directions_result["routes"][0]["legs"][0]["steps"]

#     # Make coords for the starting location of the first step.
#     lat = steps[0]["start_location"]["lat"]
#     lng = steps[0]["start_location"]["lng"]
#     start_location = (lat, lng)

#     start_time = format_time(start_location, departure_time)
#     if departure_day == "tomorrow":
#         start_time = start_time.add(days=1)

#     # Add starting location coordinates and formatted departure time to list of
#     # (coord, datetime) tuples.
#     coords_time.append((start_location, start_time))

#     # Get trip duration in seconds.
#     overall_duration = int(directions_result["routes"][0]["legs"][0]["duration"]["value"])

#     # If trip is shorter than 15 minutes, just pick middle coord.
#     if overall_duration < size_of_bucket:
#         for step in steps:
#             step_duration = int(step["duration"]["value"])

#             # If taking this step would put you over the halfway point:
#             if (time_elapsed + step_duration) > overall_duration/2:

#                 # Pick middle (or if len(paths) is even, one past) path coord.
#                 index = len(step["path"])/2

#                 # Make coords.
#                 lat = step["path"][index]["lat"]
#                 lng = step["path"][index]["lng"]
#                 coords = (lat, lng)

#                 # Divide step's duration by intervals in path.
#                 seconds_per_interval = step_duration / len(step["path"])-1

#                 # Add seconds up to selected coord.
#                 time_elapsed += (seconds_per_interval * index)
#                 time = start_time.add(seconds=time_elapsed)

#                 # Append coords, time to list.
#                 coords_time.append((coords, time))

#                 # Add time for rest of step.
#                 time_elapsed += seconds_per_interval * ((len(step["path"])-1 - index))
#                 break
#             else:
#                 time_elapsed += step_duration

#     else:
#         time_elapsed = 0
#         time_in_bucket = 0
#         for step in steps:
#             print "\nI'm starting on a step!"
#             fill_buckets(step, size_of_bucket, time_in_bucket, time_elapsed, start_time, coords_time)

#     # Make coords for the ending location of the last step.
#     lat = steps[-1]["end_location"]["lat"]
#     lng = steps[-1]["end_location"]["lng"]
#     end_location = (lat, lng)

#     end_time = start_time.add(seconds=overall_duration)
#     coords_time.append((end_location, end_time))

#     return coords_time


SIZE_OF_BUCKET = 120


class Route(object):

    def __init__(self, directions_result, departure_time, departure_day):
        self.directions_result = directions_result
        self.steps = directions_result["routes"][0]["legs"][0]["steps"]
        self.departure_time = departure_time
        self.departure_day = departure_day
        self.time_in_bucket = 0
        self.time_elapsed = 0
        self.size_of_bucket = SIZE_OF_BUCKET
        self.overall_duration = int(directions_result["routes"][0]["legs"][0]["duration"]["value"])

        # Make coords for the starting location of the first step.
        lat = self.steps[0]["start_location"]["lat"]
        lng = self.steps[0]["start_location"]["lng"]
        start_location = (lat, lng)

        self.start_time = format_time(start_location, self.departure_time)
        if self.departure_day == "tomorrow":
            self.start_time = self.start_time.add(days=1)

        # Add starting location coordinates and formatted departure time to list of
        # (coord, datetime) tuples.
        self.coords_time = [(start_location, self.start_time)]

    def make_coords_time(self):

        # If trip is shorter than 15 minutes, just pick middle coord.
        if self.overall_duration < self.size_of_bucket:
            for step in self.steps:
                step_duration = int(step["duration"]["value"])

                # If taking this step would put you over the halfway point:
                if (self.time_elapsed + self.step_duration) > self.overall_duration/2:

                    # Pick middle (or if len(paths) is even, one past) path coord.
                    index = len(step["path"])/2

                    # Make coords.
                    lat = step["path"][index]["lat"]
                    lng = step["path"][index]["lng"]
                    coords = (lat, lng)

                    # Divide step's duration by intervals in path.
                    seconds_per_interval = step_duration / len(step["path"])-1

                    # Add seconds up to selected coord.
                    self.time_elapsed += (seconds_per_interval * index)
                    time = start_time.add(seconds=self.time_elapsed)

                    # Append coords, time to list.
                    self.coords_time.append((coords, time))

                    # Add time for rest of step.
                    self.time_elapsed += seconds_per_interval * ((len(step["path"])-1 - index))
                    break
                else:
                    self.time_elapsed += step_duration

        else:
            for step in self.steps:
                print "\nI'm starting on a step!"
                self.fill_buckets(step)

        # Make coords for the ending location of the last step.
        lat = self.steps[-1]["end_location"]["lat"]
        lng = self.steps[-1]["end_location"]["lng"]
        end_location = (lat, lng)

        end_time = self.start_time.add(seconds=self.overall_duration)
        self.coords_time.append((end_location, end_time))

        return self.coords_time

    def fill_buckets(self, step):
        """Given a step, fills buckets to get middle coords."""

        step_duration = int(step["duration"]["value"])

        if (self.time_in_bucket + step_duration) < self.size_of_bucket:
            print "I fit in the bucket!"

            self.time_in_bucket = self.time_in_bucket + step_duration
            self.time_elapsed = self.time_elapsed + step_duration

            print "step duration", step_duration
            print "time in bucket", self.time_in_bucket
            print "time elapsed", self.time_elapsed

            return

        elif (self.time_in_bucket + step_duration) == self.size_of_bucket:
            print "I exactly fill the bucket!"

            self.time_in_bucket += step_duration
            self.time_elapsed += step_duration

            lat = step["end_location"]["lat"]
            lng = step["end_location"]["lng"]
            end_location = (lat, lng)

            time = self.start_time.add(seconds=self.time_elapsed)
            self.coords_time.append((end_location, time))

            print "step duration", step_duration
            print "time in bucket", self.time_in_bucket
            print "time elapsed", self.time_elapsed

            self.time_in_bucket = 0  # Empty the bucket.

            return

        else:
            print "I'm too big!"

            needed_time = self.size_of_bucket - self.time_in_bucket
            self.time_elapsed += needed_time

            fraction_needed = needed_time / float(step_duration)  # Don't floor this fraction.

            index = int(fraction_needed * len(step["path"]))  # Indices must be ints.
            lat = step["path"][index]["lat"]
            lng = step["path"][index]["lng"]
            location = (lat, lng)

            time = self.start_time.add(seconds=self.time_elapsed)
            self.coords_time.append((location, time))

            print "step duration", step_duration
            print "time in bucket", self.time_in_bucket
            print "time elapsed", self.time_elapsed

            self.time_in_bucket = 0  # Empty the bucket.

            sliced_step = slice_step(step, fraction_needed)
            self.fill_buckets(sliced_step)


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

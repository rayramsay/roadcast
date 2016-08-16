import os
import googlemaps
import forecastio
import pendulum
import json

# Remember to ``source secrets.sh``!

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])
fio_key = os.environ['FORECAST_API_KEY']

### GLOBALS ###

SIZE_OF_BUCKET = 900  # Get coords every fifteen minutes (900 seconds).


def dictify(directions_result):
    """Given directions_result as a string, make it into a dictionary."""
    return json.loads(directions_result)


#FIXME: Does this still get used anywhere?
# def get_lat_lng(loc_string):
#     """Given location as a human-readable string, return its latitude and
#     longitude as a tuple of floats."""

#     geocode_result = gmaps.geocode(loc_string)
#     lat = float(geocode_result[0]["geometry"]["location"]["lat"])
#     lng = float(geocode_result[0]["geometry"]["location"]["lng"])
#     tup = (lat, lng)

#     return tup


def format_time(coords, time):
    """Given a lat/lng tuple and time as a string, return a timezone-aware
    Pendulum datetime object."""

    timezone_result = gmaps.timezone(coords)
    timezone_id = timezone_result["timeZoneId"]

    # Note that the time's date will be the current date in that timezone.
    time = pendulum.parse(time, timezone_id)

    return time


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
        u'path': step["path"][index + 1:],  # We already used the path at that index.
        u'end_location': step["end_location"]}
    return sliced_step


class Route(object):

    def __init__(self, directions_result, departure_time, departure_day):
        """Given directions_result dictionary, departure_time string, and
        departure_day, initialize route object."""

        self.steps = directions_result["routes"][0]["legs"][0]["steps"]

        self.time_in_bucket = 0
        self.time_elapsed = 0
        self.size_of_bucket = SIZE_OF_BUCKET

        # Get trip duration in seconds.
        self.overall_duration = int(directions_result["routes"][0]["legs"][0]["duration"]["value"])

        # Make coords for the starting location of the first step.
        lat = self.steps[0]["start_location"]["lat"]
        lng = self.steps[0]["start_location"]["lng"]
        start_location = (lat, lng)

        self.start_time = format_time(start_location, departure_time)
        if departure_day == "tomorrow":
            self.start_time = self.start_time.add(days=1)

        # Add starting location coords and formatted departure time to list of
        # (coord, datetime) tuples.
        self.coords_time = [(start_location, self.start_time)]

    def make_coords_time(self):
        """Add middle and ending coords, datetime tuples to route object."""

        # If trip is shorter than 15 minutes, just pick middle coord.
        if self.overall_duration < self.size_of_bucket:
            print "I'm only getting the middle coords!"
            for step in self.steps:
                step_duration = int(step["duration"]["value"])

                # If taking this step would put you over the halfway point:
                if (self.time_elapsed + step_duration) > self.overall_duration/2:

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
                    time = self.start_time.add(seconds=self.time_elapsed)

                    # Append coords, time to list.
                    self.coords_time.append((coords, time))
                    break

                else:
                    self.time_elapsed += step_duration

        else:
            for step in self.steps:
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

            self.time_in_bucket += step_duration
            self.time_elapsed += step_duration

            return

        elif (self.time_in_bucket + step_duration) == self.size_of_bucket:

            self.time_in_bucket += step_duration
            self.time_elapsed += step_duration

            lat = step["end_location"]["lat"]
            lng = step["end_location"]["lng"]
            end_location = (lat, lng)

            time = self.start_time.add(seconds=self.time_elapsed)
            self.coords_time.append((end_location, time))

            self.time_in_bucket = 0  # Empty the bucket.

            return

        else:

            needed_time = self.size_of_bucket - self.time_in_bucket
            self.time_elapsed += needed_time

            fraction_needed = needed_time / float(step_duration)  # Don't floor this fraction.

            index = int(fraction_needed * len(step["path"]))  # Indices must be ints.
            lat = step["path"][index]["lat"]
            lng = step["path"][index]["lng"]
            location = (lat, lng)

            time = self.start_time.add(seconds=self.time_elapsed)
            self.coords_time.append((location, time))

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

        print forecast.time
        print forecast.summary, forecast.icon
        print forecast.precipProbability
        print forecast.precipIntensity

        if forecast.precipIntensity > 0:
            print forecast.precipType  # This is only defined if intensity > 0.

        print forecast.temperature
        print forecast.cloudCover

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

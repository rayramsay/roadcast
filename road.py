import os
import googlemaps
import forecastio
import pendulum
import json

############# GLOBALS ##############

# Remember to ``source secrets.sh``!

GMAPS = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])
FIO_KEY = os.environ['FORECAST_API_KEY']

####################################


def dictify(directions_result):
    """Given directions_result as a string, make it into a dictionary."""
    return json.loads(directions_result)


def format_time(coords, time):
    """Given a lat/lng tuple and time as a string, return a timezone-aware
    Pendulum datetime object."""

    timezone_result = GMAPS.timezone(coords)
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
        % (FIO_KEY, lat, lng, time)

    return forecastio.manual(url)


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

        # Get trip duration in seconds.
        self.overall_duration = int(directions_result["routes"][0]["legs"][0]["duration"]["value"])

        if self.overall_duration < 7200:  # If trip duration less than 2 hrs (7200 sec):
            self.size_of_bucket = 900  # Get coords every fifteen minutes (900 sec).
            print "Trip is shorter than two hours; getting coords every 15 minutes."

        elif self.overall_duration < 28800:  # If trip duration less than 8 hrs (28800 sec):
            self.size_of_bucket = 1800  # Get coords every thirty minutes (1800 sec).
            print "Trip is longer than two but less than eight hours; getting coords every 30 minutes."

        else:
            self.size_of_bucket = 3600  # Get coords every hour (3600 sec).
            print "Trip is longer than eight hours; getting coords every hour."

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

        # If trip is shorter than fifteen minutes, just pick middle coord.
        if self.overall_duration < 900:
            print "Trip is shorter than fifteen minutes; only getting the middle coords."
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
    """Given a list of coords/time tuples, construct a list of weather
    forecasts at those coords and times."""

    results = []

    for tup in coords_time:

        coords = tup[0]
        time = tup[1]

        forecast = get_forecast(coords, time)

        lat = coords[0]
        lng = coords[1]

        # Check timezone at coordinates.
        # timezone_result = GMAPS.timezone(coords)
        # time = time.in_timezone(timezone_result["timeZoneId"])
        time = time.format('%-I:%M %p %Z')

        # Check to see if forecast was returned.
        if forecast.response.reason == "OK":
            status = "OK"

            forecast = forecast.currently()

            summary = forecast.summary
            icon = forecast.icon
            precip_prob = forecast.precipProbability
            precip_intensity = forecast.precipIntensity
            if forecast.precipIntensity > 0:
                precip_type = forecast.precipType  # This is only defined if intensity > 0.
            else:
                precip_type = None
            temp = round(forecast.temperature)
            cloud_cover = forecast.cloudCover

            results.append({"fStatus": status,
                            "lat": lat,
                            "lng": lng,
                            "fTime": time,
                            "fSummary": summary,
                            "fIcon": icon,
                            "fPrecipProb": precip_prob,
                            "fPrecipIntensity": precip_intensity,
                            "fPrecipType": precip_type,
                            "fTemp": temp,
                            "fCloudCover": cloud_cover})

        else:
            status = "Forecast not available."

            results.append({"fStatus": status,
                            "lat": lat,
                            "lng": lng,
                            "fTime": time})

    return results

####################################

#FIXME: Does this still get used anywhere?
def convert_time(time):
    """Given a datetime object from Forecast.io, (e.g., forecast.time), convert
    to a timezone-aware Pendulum datetime object."""

    return pendulum.instance(time)


#FIXME: Does this still get used anywhere?
def get_lat_lng(loc_string):
    """Given location as a human-readable string, return its latitude and
    longitude as a tuple of floats."""

    geocode_result = GMAPS.geocode(loc_string)
    lat = float(geocode_result[0]["geometry"]["location"]["lat"])
    lng = float(geocode_result[0]["geometry"]["location"]["lng"])
    tup = (lat, lng)

    return tup

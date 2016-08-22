import os
import googlemaps
import forecastio
import pendulum
from collections import Counter

############# GLOBALS ##############

# Remember to ``source secrets.sh``!

GMAPS = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])
FIO_KEY = os.environ['FORECAST_API_KEY']


######## ROUTE CLASS + Help ########

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

        # Add starting location coords and departure datetime object to list of
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


def format_time(coords, time):
    """Given a lat/lng tuple and time as a string, return a timezone-aware
    Pendulum datetime object."""

    timezone_result = GMAPS.timezone(coords)
    timezone_id = timezone_result["timeZoneId"]

    # Note that the time's date will be the current date in that timezone.
    datetime = pendulum.parse(time, timezone_id)

    return datetime

def slice_step(step, fraction_needed):
    """Cuts off part of step."""
    index = int(fraction_needed * len(step["path"]))  # Indices must be ints.
    sliced_step = {
        u'duration': {u'value': int(step["duration"]["value"]) * (1 - fraction_needed)},
        u'path': step["path"][index + 1:],  # We already used the path at that index.
        u'end_location': step["end_location"]}
    return sliced_step




####################################
# Weather
####################################

def get_forecast(coords, time):
    """Given lat/lng tuple and Pendulum datetime object, return forecast."""

    lat = coords[0]
    lng = coords[1]

    # Convert to ISO 8601 string.
    time = time.to_iso8601_string()

    url = 'https://api.forecast.io/forecast/%s/%s,%s,%s' \
        % (FIO_KEY, lat, lng, time)

    return forecastio.manual(url)

def make_marker_info(coords_time):
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
            precip_prob *= 100  # Turn into percentage points.
            # precip_prob = round(precip_prob)

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


def make_weather_report(weather_results):
    """Given a list of weather result dictionaries, generate a weather report
    dictionary for the trip."""

    weather_report = {}
    precip_types = ["snow", "rain", "sleet"]

    mode = modal_weather(weather_results)
    weather_report["modalWeather"] = mode

    avg = avg_temp(weather_results)
    weather_report["avgTemp"] = round(avg)

    cum_precip_prob = precip_prob(weather_results) * 100  # Turn into percentage points.
    weather_report["precipProb"] = round(cum_precip_prob)

    for p_type in precip_types:
        key = p_type + "Prob"
        cum_type_prob = type_prob(weather_results, p_type) * 100  # Turn into percentage points.
        weather_report[key] = round(cum_type_prob)

    maxi = max_intensity(weather_results)
    weather_report["maxIntensity"] = maxi

    for p_type in precip_types:
        key = p_type + "Max"
        max_type = type_max(weather_results, p_type)
        weather_report[key] = max_type

    return weather_report


def modal_weather(weather_results):
    """Given a list of weather result dictionaries, returns the modal weather as
    a string.

    In the event of multi-modality, chooses an arbitrary mode."""

    cnt = Counter()
    cnt[u'Rainy'] = 0
    cnt[u'Cloudy'] = 0
    rainy = [u'Drizzle', u'Light Rain']
    cloudy = [u'Partly Cloudy', u'Mostly Cloudy']

    for result in weather_results:
        summary = result["fSummary"]
        cnt[summary] += 1

    for key in cnt.iterkeys():
        if key in rainy:
            cnt[u'Rainy'] += cnt[key]
        if key in cloudy:
            cnt[u'Cloudy'] += cnt[key]

    mode = cnt.most_common()
    print mode

    mode = mode[0][0].lower()

    return mode


def avg_temp(weather_results):
    """Given a list of weather result dictionaries, returns the average
    temperature as a float."""

    numerator = 0
    denominator = len(weather_results)
    for result in weather_results:
        temp = result["fTemp"]
        numerator += temp
    mean = numerator/denominator

    return mean


def precip_prob(weather_results):
    """Given a list of weather result dictionaries, returns the probability of
    precipitation for the whole trip."""

    # The probability of no precipitation occurring at a specific point is
    # (1 - precip_prob). The cumulative probability of no precipitation is each
    # point's no-precip prob multiplied together. Thus the probability of at
    # least one incident of precipitation is 1 - the product of no-precip probs.

    cum_no_precip_prob = 1
    for result in weather_results:
        precip_prob = result["fPrecipProb"]/100.0  # Turn back into a decimal.
        cum_no_precip_prob *= (1 - precip_prob)
    cum_precip_prob = 1 - cum_no_precip_prob
    return cum_precip_prob


def type_prob(weather_results, precip_type):
    """Given a list of weather result dictionaries and a type of precipitation
    as a string, returns the probability of that particular type for the whole
    trip."""

    cum_no_precip_prob = 1
    for result in weather_results:
        p_type = result.get("fPrecipType")
        if p_type == precip_type:
            precip_prob = result["fPrecipProb"]/100.0  # Turn back into a decimal.
        else:
            precip_prob = 0
        cum_no_precip_prob *= (1 - precip_prob)
    cum_precip_prob = 1 - cum_no_precip_prob
    return cum_precip_prob


def max_intensity(weather_results):
    """Given a list of weather result dictionaries, returns the maximum
    precipitation intensity out of the whole trip."""

    max_intensity = 0
    for result in weather_results:
        if result["fPrecipIntensity"] > max_intensity:
            max_intensity = result["fPrecipIntensity"]

    return max_intensity


def type_max(weather_results, precip_type):
    """Given a list of weather result dictionaries and a type of precipitation
    as a string, returns the maximum precipitation intensity of that particular
    type for the whole trip."""

    max_intensity = 0
    for result in weather_results:
        p_type = result.get("fPrecipType")
        if p_type == precip_type and result["fPrecipIntensity"] > max_intensity:
            max_intensity = result["fPrecipIntensity"]

    return max_intensity


def normalize(value, vmin, vmax):
    normalized = (value - vmin) / (vmax - vmin)
    return normalized


def normalized_intensity(intensity):
    """Normalize an intensity to between 0 and 1."""

    # normalized = ( x - min(x) ) / ( max(x) - min(x) )
    # theoretical maximum intensity is 0.5
    # therefore:

    normalized = intensity/0.5
    return normalized


def avg_intensity(weather_results):
    """Given a list of weather result dictionaries, returns the average
    precipitation intensity."""

    numerator = 0
    denominator = len(weather_results)
    for result in weather_results:
        intensity = result["fPrecipIntensity"]
        numerator += intensity
    mean = numerator/denominator

    return mean


def make_result(directions_result, departure_time, departure_day):
    """Builds the dictionary for jsonification."""

    result = {}

    # Instantiate route object.
    timed_route = Route(directions_result, departure_time, departure_day)

    # print timed_route

    # Make list of coordinates and datetimes.
    coords_time = timed_route.make_coords_time()

    print coords_time

    # Get weather info for coords and times.
    marker_info = make_marker_info(coords_time)

    # print marker_info

    # Make weather report for trip.
    weather_report = make_weather_report(marker_info)

    # print weather_report

    result["markerInfo"] = marker_info
    result["weatherReport"] = weather_report

    # print result

    return result


def make_score(weather_results):
    """Calculate ``badness`` of weather score."""

    pass



####################################

#FIXME: Does this still get used anywhere?
# def convert_time(time):
    """Given a datetime object from Forecast.io, (e.g., forecast.time), convert
    to a timezone-aware Pendulum datetime object."""

    return pendulum.instance(time)


#FIXME: Does this still get used anywhere?
# def get_lat_lng(loc_string):
    """Given location as a human-readable string, return its latitude and
    longitude as a tuple of floats."""

    geocode_result = GMAPS.geocode(loc_string)
    lat = float(geocode_result[0]["geometry"]["location"]["lat"])
    lng = float(geocode_result[0]["geometry"]["location"]["lng"])
    tup = (lat, lng)

    return tup

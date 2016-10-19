import os
import forecastio
#import googlemaps
#import pendulum

from collections import Counter

############# GLOBALS ##############

# Remember to ``source secrets.sh``!

#GMAPS = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])
FIO_KEY = os.environ['FORECAST_API_KEY']

####################################


def make_marker_info(coords_time):
    """Given a list of (coords, time) tuples, constructs a list of weather
    forecasts at those coords and times."""

    marker_info = []

    for tup in coords_time:

        coords, time = tup

        forecast = get_forecast(coords, time)

        lat, lng = coords

        # Check timezone at coordinates.
        # timezone_result = GMAPS.timezone(coords)
        # time = time.in_timezone(timezone_result["timeZoneId"])

        # Format time as 12-hour Hour:zero-padded Minute AM/PM Timezone.
        time = time.format('%-I:%M %p %Z')

        # Check to see if forecast was returned.
        if forecast.response.reason == "OK":

            status = "OK"

            forecast = forecast.currently()

            summary = forecast.summary
            icon = forecast.icon

            temp = round(forecast.temperature)

            precip_prob = forecast.precipProbability * 100  # Turn into percentage points.

            precip_intensity = forecast.precipIntensity

            if forecast.precipIntensity > 0:
                precip_type = forecast.precipType  # This is only defined if intensity > 0.
            else:
                precip_type = None

            # cloud_cover = forecast.cloudCover

            marker_info.append({"fStatus": status,
                                "lat": lat,
                                "lng": lng,
                                "fTime": time,
                                "fSummary": summary,
                                "fIcon": icon,
                                "fPrecipProb": precip_prob,
                                "fPrecipIntensity": precip_intensity,
                                "fPrecipType": precip_type,
                                "fTemp": temp})

        else:
            status = "Forecast not available."

            marker_info.append({"fStatus": status,
                                "lat": lat,
                                "lng": lng,
                                "fTime": time})

    return marker_info


def get_forecast(coords, time):
    """Given (lat, lng) tuple and Pendulum datetime object, returns forecast."""

    lat, lng = coords

    # Convert datetime object to ISO 8601 string.
    time = time.to_iso8601_string()

    url = 'https://api.darksky.net/forecast/%s/%s,%s,%s' \
        % (FIO_KEY, lat, lng, time)

    return forecastio.manual(url)


def make_weather_report(weather_results):
    """Given a list of weather result dictionaries, generates a weather report
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

    # avgi = avg_intensity(weather_results)
    # weather_report["avgIntensity"] = avgi

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

    ordered_by_count = cnt.most_common()
    # print ordered_by_count

    mode = ordered_by_count[0][0].lower()

    if mode == "mostly cloudy":
        mode = "cloudy"

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


def avg_intensity(weather_results):
    """Given a list of weather result dictionaries, returns the average
    precipitation intensity as a float."""

    numerator = 0
    denominator = len(weather_results)

    for result in weather_results:
        intensity = result["fPrecipIntensity"]
        numerator += intensity

    mean = numerator/denominator

    return mean

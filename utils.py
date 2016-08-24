import json
# import pendulum


def dictify(directions_result):
    """Given directions_result as a unicode string, make it into a dictionary."""
    return json.loads(directions_result)


def normalize(value, vmin, vmax):
    """Given a value and its min and max, normalize that value."""
    normalized = (value - vmin) / (vmax - vmin)
    return normalized


####################################

#FIXME: Does this still get used anywhere?
def convert_time(time):
    """Given a datetime object from Forecast.io, (e.g., forecast.time), convert
    to a timezone-aware Pendulum datetime object."""

    return pendulum.instance(time)

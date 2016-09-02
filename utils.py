import json


def dictify(directions_result):
    """Given directions_result as a unicode string, make it into a dictionary."""
    return json.loads(directions_result)


def normalize(value, vmin, vmax):
    """Given a value and its min and max, rescale that value."""
    normalized = (value - vmin) / (vmax - vmin)
    return normalized

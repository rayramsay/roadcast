import json


def dictify(directions_result):
    """Given directions_result as a unicode string, make it into a dictionary."""
    return json.loads(directions_result)

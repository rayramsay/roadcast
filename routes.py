import os
import googlemaps
import pendulum

############# GLOBALS ##############
# Remember to ``source secrets.sh``!
GMAPS = googlemaps.Client(key=os.environ['GOOGLE_API_SERVER_KEY'])
####################################


class Route(object):

    def __init__(self, directions_prepped, departure_time, departure_day):
        """Given directions_prepped dictionary, departure_time string, and
        departure_day string, initializes Route object."""

        self.steps = directions_prepped["steps"]
        self.overall_duration = directions_prepped["duration"]

        self.total_time_elapsed = 0
        self.interval_time_elapsed = 0

        # Set interval between coords based on overall duration.
        self.interval_size = Route.get_interval_size(self.overall_duration)

        # Make coords for the starting location of the first step.
        lat = self.steps[0]["start_location"]["lat"]
        lng = self.steps[0]["start_location"]["lng"]
        start_location = (lat, lng)

        self.start_time = Route.format_time(start_location, departure_time, departure_day)

        # Add starting location coords and departure datetime object to list of
        # (coords, datetime) tuples.
        self.coords_time = [(start_location, self.start_time)]

    def make_coords_time(self):
        """Add middle and ending (coords, datetime) tuples to route object."""

        # If trip is shorter than fifteen minutes, just pick middle coord.
        if self.overall_duration < 900:
            self.pick_middle()

        else:
            for step in self.steps:
                self.get_next_coords_time(step)

        # Make coords for the ending location of the last step.
        lat = self.steps[-1]["end_location"]["lat"]
        lng = self.steps[-1]["end_location"]["lng"]
        end_location = (lat, lng)

        end_time = self.start_time.add(seconds=self.overall_duration)
        self.coords_time.append((end_location, end_time))

        return self.coords_time

    def pick_middle(self):
        """Adds middle coords and datetime to coords_time."""

        for step in self.steps:
                step_duration = int(step["duration"]["value"])

                # If taking this step keeps you below the halfway point:
                if (self.total_time_elapsed + step_duration) < self.overall_duration/2:
                    self.total_time_elapsed += step_duration

                else:
                    # Pick middle (or if len(paths) is even, one past) path coords.
                    index = len(step["path"])/2

                    # Make coords.
                    lat = step["path"][index]["lat"]
                    lng = step["path"][index]["lng"]
                    coords = (lat, lng)

                    # Divide step's duration by intervals in path.
                    seconds_per_interval = step_duration / (len(step["path"]) - 1)

                    # Add seconds up to selected coord.
                    self.total_time_elapsed += (seconds_per_interval * index)
                    time = self.start_time.add(seconds=self.total_time_elapsed)

                    # Append coords, time to list.
                    self.coords_time.append((coords, time))
                    return

    def get_next_coords_time(self, step):
        """Given a step, checks to see if its duration fits within the current
        interval. If not, calculates how far into the step the interval finishes,
        and gets coordinates and datetime at that point."""

        step_duration = int(step["duration"]["value"])

        if (self.interval_time_elapsed + step_duration) < self.interval_size:

            self.interval_time_elapsed += step_duration
            self.total_time_elapsed += step_duration

            return

        elif (self.interval_time_elapsed + step_duration) == self.interval_size:

            self.total_time_elapsed += step_duration

            lat = step["end_location"]["lat"]
            lng = step["end_location"]["lng"]
            end_location = (lat, lng)

            time = self.start_time.add(seconds=self.total_time_elapsed)
            self.coords_time.append((end_location, time))

            return

        else:

            needed_time = self.interval_size - self.interval_time_elapsed
            self.total_time_elapsed += needed_time

            fraction_needed = needed_time / float(step_duration)  # Don't floor this fraction.

            index = int(fraction_needed * len(step["path"]))  # Indices must be ints.
            lat = step["path"][index]["lat"]
            lng = step["path"][index]["lng"]
            location = (lat, lng)

            time = self.start_time.add(seconds=self.total_time_elapsed)
            self.coords_time.append((location, time))

            self.interval_time_elapsed = 0  # Reset interval.

            sliced_step = Route.slice_step(step, fraction_needed)
            self.get_next_coords_time(sliced_step)

    @staticmethod
    def get_interval_size(overall_duration):
        """Given overall_duration in seconds, choose appropriate interval between coords."""

        if overall_duration < 7200:  # If trip duration less than 2 hrs (7200 sec):
            interval_size = 900  # Get coords every fifteen minutes (900 sec).

        elif overall_duration < 28800:  # If trip duration less than 8 hrs (28800 sec):
            interval_size = 1800  # Get coords every thirty minutes (1800 sec).

        else:
            interval_size = 3600  # Else: Get coords every hour (3600 sec).

        return interval_size

    @staticmethod
    def format_time(coords, time_string, day_string):
        """Given a lat/lng tuple and time and day as strings, returns a timezone-
        aware Pendulum datetime object."""

        # Make an API call to find the location's timezone.
        timezone_result = GMAPS.timezone(coords)
        timezone_id = timezone_result["timeZoneId"]

        # Note that upon instantiation, the date will be the current date in that timezone.
        datetime = pendulum.parse(time_string, timezone_id)

        if day_string == "tomorrow":
            datetime = datetime.add(days=1)

        return datetime

    @staticmethod
    def slice_step(step, fraction_needed):
        """Cuts off the part of the step that was already processed."""

        index = int(fraction_needed * len(step["path"]))  # Indices must be ints.

        sliced_step = {
            u'duration': {u'value': int(step["duration"]["value"]) * (1 - fraction_needed)},
            u'path': step["path"][index + 1:],  # We already used the coordinates at that index.
            u'end_location': step["end_location"]}

        return sliced_step

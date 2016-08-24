import unittest
import pendulum

from routes import Route
import road

# FIXME: Put DIRECTIONS_RESULT into setup.

DIRECTIONS_RESULT_899 = {u'routes': [{u'legs': [{u'duration': {u'value': 899}, u'start_location': {u'lat': 1, u'lng': 100}, u'end_location': {u'lat': 1, u'lng': 129}, u'steps': [{u'duration': {u'value': 400}, u'start_location': {u'lat': 1, u'lng': 100}, u'end_location': {u'lat': 1, u'lng': 110}, u'path': [{u'lat': 1, u'lng': 100}, {u'lat': 1, u'lng': 101}, {u'lat': 1, u'lng': 102}, {u'lat': 1, u'lng': 103}, {u'lat': 1, u'lng': 104}, {u'lat': 1, u'lng': 105}, {u'lat': 1, u'lng': 106}, {u'lat': 1, u'lng': 107}, {u'lat': 1, u'lng': 108}, {u'lat': 1, u'lng': 109}, {u'lat': 1, u'lng': 110}]}, {u'duration': {u'value': 300}, u'start_location': {u'lat': 1, u'lng': 110}, u'end_location': {u'lat': 1, u'lng': 120}, u'path': [{u'lat': 1, u'lng': 110}, {u'lat': 1, u'lng': 111}, {u'lat': 1, u'lng': 112}, {u'lat': 1, u'lng': 113}, {u'lat': 1, u'lng': 114}, {u'lat': 1, u'lng': 115}, {u'lat': 1, u'lng': 116}, {u'lat': 1, u'lng': 117}, {u'lat': 1, u'lng': 118}, {u'lat': 1, u'lng': 119}, {u'lat': 1, u'lng': 120}]}, {u'duration': {u'value': 199}, u'start_location': {u'lat': 1, u'lng': 120}, u'end_location': {u'lat': 1, u'lng': 129}, u'path': [{u'lat': 1, u'lng': 120}, {u'lat': 1, u'lng': 121}, {u'lat': 1, u'lng': 122}, {u'lat': 1, u'lng': 123}, {u'lat': 1, u'lng': 124}, {u'lat': 1, u'lng': 125}, {u'lat': 1, u'lng': 126}, {u'lat': 1, u'lng': 127}, {u'lat': 1, u'lng': 128}, {u'lat': 1, u'lng': 129}]}]}]}]}
DIRECTIONS_RESULT_1999 = {u'routes': [{u'legs': [{u'duration': {u'value': 1999}, u'start_location': {u'lat': 1, u'lng': 100}, u'end_location': {u'lat': 1, u'lng': 129}, u'steps': [{u'duration': {u'value': 800}, u'start_location': {u'lat': 1, u'lng': 100}, u'end_location': {u'lat': 1, u'lng': 110}, u'path': [{u'lat': 1, u'lng': 100}, {u'lat': 1, u'lng': 101}, {u'lat': 1, u'lng': 102}, {u'lat': 1, u'lng': 103}, {u'lat': 1, u'lng': 104}, {u'lat': 1, u'lng': 105}, {u'lat': 1, u'lng': 106}, {u'lat': 1, u'lng': 107}, {u'lat': 1, u'lng': 108}, {u'lat': 1, u'lng': 109}, {u'lat': 1, u'lng': 110}]}, {u'duration': {u'value': 1000}, u'start_location': {u'lat': 1, u'lng': 110}, u'end_location': {u'lat': 1, u'lng': 120}, u'path': [{u'lat': 1, u'lng': 110}, {u'lat': 1, u'lng': 111}, {u'lat': 1, u'lng': 112}, {u'lat': 1, u'lng': 113}, {u'lat': 1, u'lng': 114}, {u'lat': 1, u'lng': 115}, {u'lat': 1, u'lng': 116}, {u'lat': 1, u'lng': 117}, {u'lat': 1, u'lng': 118}, {u'lat': 1, u'lng': 119}, {u'lat': 1, u'lng': 120}]}, {u'duration': {u'value': 199}, u'start_location': {u'lat': 1, u'lng': 120}, u'end_location': {u'lat': 1, u'lng': 129}, u'path': [{u'lat': 1, u'lng': 120}, {u'lat': 1, u'lng': 121}, {u'lat': 1, u'lng': 122}, {u'lat': 1, u'lng': 123}, {u'lat': 1, u'lng': 124}, {u'lat': 1, u'lng': 125}, {u'lat': 1, u'lng': 126}, {u'lat': 1, u'lng': 127}, {u'lat': 1, u'lng': 128}, {u'lat': 1, u'lng': 129}]}]}]}]}


class RouteStaticMethodsTestCase(unittest.TestCase):

    def test_get_bucket_size(self):
        # Check for overall duration of one hour (i.e., less than two hours).
        result = Route.get_bucket_size(3600)
        self.assertEqual(result, 900)

        # Check for overall duration of three hours (i.e., more than two but less than eight hours).
        result = Route.get_bucket_size(10800)
        self.assertEqual(result, 1800)

        # Check for overall duration of nine hours (i.e., more than eight hours).
        result = Route.get_bucket_size(32400)
        self.assertEqual(result, 3600)

    def test_format_time(self):
        result = Route.format_time((40.7480779, -73.9848399), "03:01", "tomorrow")

        # Check that it's an instance of a Pendulum object.
        self.assertIsInstance(result, pendulum.pendulum.Pendulum)

        # Check that it has the correct timezone.
        self.assertTrue(result.timezone_name, 'America/New_York')

        # Check that departure_day (``tomorrow``) has been set correctly.
        self.assertTrue(result.is_tomorrow())

        # Check that it has the correct hour and minutes.
        self.assertEqual(result.hour, 3)
        self.assertEqual(result.minute, 1)

    def test_slice_step(self):
        result = Route.slice_step(road.prep_directions(DIRECTIONS_RESULT_1999)["steps"][1], 0.1)

        # Check that the new duration is correct.
        self.assertEqual(result["duration"]["value"], 900)

        # Check that the correct number of paths are left.
        self.assertEqual(len(result["path"]), 9)

        # Check that it still has the end location.
        self.assertEqual(result["end_location"], road.prep_directions(DIRECTIONS_RESULT_1999)["steps"][1]["end_location"])


class RouteClassTestCase(unittest.TestCase):

    def test_Route_init(self):
        result = Route(road.prep_directions(DIRECTIONS_RESULT_899), "03:01", "tomorrow")

        # Check that it's an instance of a Route object.
        self.assertIsInstance(result, Route)

        # Check that it has the right number of steps.
        self.assertEqual(len(result.steps), 3)

        # Check that it has the correct overall duration.
        self.assertEqual(result.overall_duration, 899)

        # Check the initial values for time_in_bucket, time_elapsed, and size_of_bucket.
        self.assertEqual(result.time_in_bucket, 0)
        self.assertEqual(result.time_elapsed, 0)
        self.assertEqual(result.size_of_bucket, 900)

        # Check that starting location coords are in coords_time.
        self.assertIn((1, 100), result.coords_time[0])

        # Check that it has the right starting time.
        self.assertEqual(result.start_time.hour, 3)
        self.assertEqual(result.start_time.minute, 1)

    def test_Route_pick_middle(self):
        result = Route(road.prep_directions(DIRECTIONS_RESULT_899), "03:01", "tomorrow")
        coords_time = result.make_coords_time()

        # Check that it has the right number of coords.
        self.assertEqual(len(coords_time), 3)

        # Check that correct middle coord was picked.
        self.assertIn((1, 115), coords_time[1])

        # Check that correct time was paired with middle coord.
        self.assertEqual(coords_time[0][1].add(seconds=550), coords_time[1][1])

    def test_Route_fill_buckets(self):
        result = Route(road.prep_directions(DIRECTIONS_RESULT_1999), "03:01", "tomorrow")
        coords_time = result.make_coords_time()

        # Check that it has the right number of coords.
        self.assertEqual(len(coords_time), 4)

        # Check that correct middle coords were picked.
        self.assertIn((1, 111), coords_time[1])
        self.assertIn((1, 120), coords_time[2])

        # Check that second datetime is fifteen minutes past first datetime.
        self.assertEqual(coords_time[0][1].add(minutes=15), coords_time[1][1])

        # Check that third datetime is fifteen minutes past second datetime.
        self.assertEqual(coords_time[1][1].add(minutes=15), coords_time[2][1])

    def test_Route_make_coords_time(self):
        result = Route(road.prep_directions(DIRECTIONS_RESULT_899), "03:01", "tomorrow")
        coords_time = result.make_coords_time()

        # Check that ending location coords are in coords_time.
        self.assertIn((1, 129), coords_time[-1])

################################################################################

if __name__ == '__main__':
    unittest.main()

import unittest
import pendulum

import road


DIRECTIONS_RESULT = {u'routes': [{u'overview_polyline': u'oruwFfdqbMmEyCwFsDwFqDoCiBeBkAhBuFzCuJFUjB_G\\aAgC_BsA_A', u'warnings': [u'Walking directions are in beta.    Use caution \u2013 This route may be missing sidewalks or pedestrian paths.'], u'bounds': {u'west': -73.98484, u'east': -73.97575, u'north': 40.75282, u'south': 40.74808}, u'waypoint_order': [], u'summary': u'5th Ave and E 41st St', u'copyrights': u'Map data \xa92016 Google', u'legs': [{u'distance': {u'text': u'0.7 mi', u'value': 1207}, u'traffic_speed_entry': [], u'end_address': u'405 Lexington Ave, New York, NY 10174, USA', u'via_waypoint': [], u'via_waypoints': [], u'start_address': u'350 5th Ave, New York, NY 10118, USA', u'start_location': {u'lat': 40.7480779, u'lng': -73.9848399}, u'steps': [{u'distance': {u'text': u'0.4 mi', u'value': 603}, u'lat_lngs': [{u'lat': 40.74808, u'lng': -73.98484}, {u'lat': 40.748450000000005, u'lng': -73.98456}, {u'lat': 40.74911, u'lng': -73.98407}, {u'lat': 40.74973000000001, u'lng': -73.98364000000001}, {u'lat': 40.750350000000005, u'lng': -73.98317}, {u'lat': 40.750960000000006, u'lng': -73.98274}, {u'lat': 40.75159, u'lng': -73.98228}, {u'lat': 40.7522, u'lng': -73.98183}, {u'lat': 40.75231, u'lng': -73.98175}, {u'lat': 40.75282, u'lng': -73.98137000000001}], u'travel_mode': u'WALKING', u'end_point': {u'lat': 40.7528183, u'lng': -73.9813747}, u'encoded_lat_lngs': u'oruwFfdqbMiAw@cCaB{BuA{B}AyBuA}B{AyByAUOeBkA', u'start_location': {u'lat': 40.7480779, u'lng': -73.9848399}, u'polyline': {u'points': u'oruwFfdqbMiAw@cCaB{BuA{B}AyBuA}B{AyByAUOeBkA'}, u'duration': {u'text': u'8 mins', u'value': 463}, u'path': [{u'lat': 40.74808, u'lng': -73.98484}, {u'lat': 40.748450000000005, u'lng': -73.98456}, {u'lat': 40.74911, u'lng': -73.98407}, {u'lat': 40.74973000000001, u'lng': -73.98364000000001}, {u'lat': 40.750350000000005, u'lng': -73.98317}, {u'lat': 40.750960000000006, u'lng': -73.98274}, {u'lat': 40.75159, u'lng': -73.98228}, {u'lat': 40.7522, u'lng': -73.98183}, {u'lat': 40.75231, u'lng': -73.98175}, {u'lat': 40.75282, u'lng': -73.98137000000001}], u'maneuver': u'', u'end_location': {u'lat': 40.7528183, u'lng': -73.9813747}, u'start_point': {u'lat': 40.7480779, u'lng': -73.9848399}, u'instructions': u'Head <b>northeast</b> on <b>5th Ave</b> toward <b>E 34th St</b>'}, {u'distance': {u'text': u'0.3 mi', u'value': 465}, u'lat_lngs': [{u'lat': 40.75282, u'lng': -73.98137000000001}, {u'lat': 40.75229, u'lng': -73.98014}, {u'lat': 40.752140000000004, u'lng': -73.97978}, {u'lat': 40.75151, u'lng': -73.97827000000001}, {u'lat': 40.75148, u'lng': -73.97819000000001}, {u'lat': 40.75148, u'lng': -73.97818000000001}, {u'lat': 40.751470000000005, u'lng': -73.97817}, {u'lat': 40.751470000000005, u'lng': -73.97816}, {u'lat': 40.751450000000006, u'lng': -73.97812}, {u'lat': 40.75141, u'lng': -73.97803}, {u'lat': 40.750930000000004, u'lng': -73.97688000000001}, {u'lat': 40.750780000000006, u'lng': -73.97655}], u'travel_mode': u'WALKING', u'maneuver': u'turn-right', u'end_point': {u'lat': 40.7507826, u'lng': -73.97654829999999}, u'encoded_lat_lngs': u'cpvwFpnpbMhBuF\\gA|BmHDO?A@A?ABGFQ~AeF\\aA', u'start_location': {u'lat': 40.7528183, u'lng': -73.9813747}, u'polyline': {u'points': u'cpvwFpnpbMhBuF\\gA|BmHDO?A@A?ABGFQ~AeF\\aA'}, u'duration': {u'text': u'6 mins', u'value': 331}, u'path': [{u'lat': 40.75282, u'lng': -73.98137000000001}, {u'lat': 40.75229, u'lng': -73.98014}, {u'lat': 40.752140000000004, u'lng': -73.97978}, {u'lat': 40.75151, u'lng': -73.97827000000001}, {u'lat': 40.75148, u'lng': -73.97819000000001}, {u'lat': 40.75148, u'lng': -73.97818000000001}, {u'lat': 40.751470000000005, u'lng': -73.97817}, {u'lat': 40.751470000000005, u'lng': -73.97816}, {u'lat': 40.751450000000006, u'lng': -73.97812}, {u'lat': 40.75141, u'lng': -73.97803}, {u'lat': 40.750930000000004, u'lng': -73.97688000000001}, {u'lat': 40.750780000000006, u'lng': -73.97655}], u'end_location': {u'lat': 40.7507826, u'lng': -73.97654829999999}, u'start_point': {u'lat': 40.7528183, u'lng': -73.9813747}, u'instructions': u'Turn <b>right</b> onto <b>E 41st St</b>'}, {u'distance': {u'text': u'456 ft', u'value': 139}, u'lat_lngs': [{u'lat': 40.750780000000006, u'lng': -73.97655}, {u'lat': 40.75146, u'lng': -73.97607}, {u'lat': 40.751850000000005, u'lng': -73.97577000000001}, {u'lat': 40.75188, u'lng': -73.97575}], u'travel_mode': u'WALKING', u'maneuver': u'turn-left', u'end_point': {u'lat': 40.7518824, u'lng': -73.97575310000002}, u'encoded_lat_lngs': u'kcvwFlpobMgC_BmA{@EC', u'start_location': {u'lat': 40.7507826, u'lng': -73.97654829999999}, u'polyline': {u'points': u'kcvwFlpobMgC_BmA{@EC'}, u'duration': {u'text': u'2 mins', u'value': 111}, u'path': [{u'lat': 40.750780000000006, u'lng': -73.97655}, {u'lat': 40.75146, u'lng': -73.97607}, {u'lat': 40.751850000000005, u'lng': -73.97577000000001}, {u'lat': 40.75188, u'lng': -73.97575}], u'end_location': {u'lat': 40.7518824, u'lng': -73.97575310000002}, u'start_point': {u'lat': 40.7507826, u'lng': -73.97654829999999}, u'instructions': u'Turn <b>left</b> onto <b>Lexington Ave</b><div style="font-size:0.9em">Destination will be on the right</div>'}], u'duration': {u'text': u'15 mins', u'value': 905}, u'end_location': {u'lat': 40.7518824, u'lng': -73.97575310000002}}], u'overview_path': [{u'lat': 40.74808, u'lng': -73.98484}, {u'lat': 40.74911, u'lng': -73.98407}, {u'lat': 40.750350000000005, u'lng': -73.98317}, {u'lat': 40.75159, u'lng': -73.98228}, {u'lat': 40.75231, u'lng': -73.98175}, {u'lat': 40.75282, u'lng': -73.98137000000001}, {u'lat': 40.75229, u'lng': -73.98014}, {u'lat': 40.75151, u'lng': -73.97827000000001}, {u'lat': 40.751470000000005, u'lng': -73.97816}, {u'lat': 40.750930000000004, u'lng': -73.97688000000001}, {u'lat': 40.750780000000006, u'lng': -73.97655}, {u'lat': 40.75146, u'lng': -73.97607}, {u'lat': 40.75188, u'lng': -73.97575}]}], u'status': u'OK', u'geocoded_waypoints': [{u'place_id': u'ChIJn6wOs6lZwokRLKy1iqRcoKw', u'geocoder_status': u'OK', u'types': [u'street_address']}, {u'place_id': u'ChIJAe73SQJZwokRHTRcoQpAhF8', u'geocoder_status': u'OK', u'types': [u'street_address']}], u'request': {u'origin': u'350 5th Ave, New York, NY 10118, United States', u'destination': u'405 Lexington Ave, New York, NY 10174, United States', u'travelMode': u'WALKING'}}

class RoadUnitTestCase(unittest.TestCase):

    def test_Route_class_init(self):
        result = road.Route(DIRECTIONS_RESULT, "03:01", "tomorrow")

        # Check that it's an instance of a Route object.
        self.assertIsInstance(result, road.Route)

        # Check that it has the correct number of steps.
        self.assertEqual(len(result.steps), 3)

        # Check that it has the correct overall duration.
        self.assertEqual(result.overall_duration, 905)

        # Check the initial values for time_in_bucket, time_elapsed, and size_of_bucket.
        self.assertEqual(result.time_in_bucket, 0)
        self.assertEqual(result.time_elapsed, 0)
        self.assertEqual(result.size_of_bucket, 900)

        # Check that starting location coords are in coords_time.
        self.assertIn((40.7480779, -73.9848399), result.coords_time[0])

        # Check that departure_day (``tomorrow``) has been set correctly.
        self.assertTrue(result.start_time.is_tomorrow())

    def test_Route_class_make_coords_time(self):
        result = road.Route(DIRECTIONS_RESULT, "03:01", "tomorrow").make_coords_time()

        # Check that it has the right number of coords.
        self.assertEqual(len(result), 3)

        # Check that ending location coords are in coords_time.
        self.assertIn((40.7518824, -73.97575310000002), result[-1])

    def test_format_time(self):
        result = road.format_time((40.7480779, -73.9848399), "03:01")

        # Check that it's an instance of a Pendulum object.
        self.assertIsInstance(result, pendulum.pendulum.Pendulum)

        # Check that the date is today.
        self.assertTrue(result.is_same_day(pendulum.now()))

        # Check that it has the correct timezone.
        self.assertTrue(result.timezone_name, 'America/New_York')

        # Check that it has the right hour and minutes.
        self.assertEqual(result.hour, 3)
        self.assertEqual(result.minute, 1)

################################################################################

if __name__ == '__main__':
    unittest.main()

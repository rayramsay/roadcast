import unittest
import pendulum

import road


DIRECTIONS_RESULT = {u'routes': [{u'overview_polyline': u'}kyeF|uziVAAGUGOyE|C\\hAdBnFrDhLxB~GFRKVOZQPEJu@d@[PwEnC', u'warnings': [], u'bounds': {u'west': -122.37379000000001, u'east': -122.36635000000001, u'north': 37.819570000000006, u'south': 37.81736}, u'waypoint_order': [], u'summary': u'California Ave and Avenue of the Palms', u'copyrights': u'Map data \xa92016 Google', u'legs': [{u'distance': {u'text': u'0.6 mi', u'value': 915}, u'traffic_speed_entry': [], u'end_address': u'Avenue of the Palms, San Francisco, CA 94130, USA', u'via_waypoint': [], u'via_waypoints': [], u'start_address': u'Clipper Cove Way, San Francisco, CA 94130, USA', u'start_location': {u'lat': 37.8183858, u'lng': -122.36654670000001}, u'steps': [{u'distance': {u'text': u'66 ft', u'value': 20}, u'lat_lngs': [{u'lat': 37.81839, u'lng': -122.36655}, {u'lat': 37.81839, u'lng': -122.36654000000001}, {u'lat': 37.818400000000004, u'lng': -122.36654000000001}, {u'lat': 37.818400000000004, u'lng': -122.36653000000001}, {u'lat': 37.81844, u'lng': -122.36643000000001}, {u'lat': 37.81848, u'lng': -122.36635000000001}], u'travel_mode': u'DRIVING', u'end_point': {u'lat': 37.818481, u'lng': -122.36635380000001}, u'encoded_lat_lngs': u'}kyeF|uziV?AA??AGSGO', u'start_location': {u'lat': 37.8183858, u'lng': -122.36654670000001}, u'polyline': {u'points': u'}kyeF|uziV?AA??AGSGO'}, u'duration': {u'text': u'1 min', u'value': 4}, u'path': [{u'lat': 37.81839, u'lng': -122.36655}, {u'lat': 37.81839, u'lng': -122.36654000000001}, {u'lat': 37.818400000000004, u'lng': -122.36654000000001}, {u'lat': 37.818400000000004, u'lng': -122.36653000000001}, {u'lat': 37.81844, u'lng': -122.36643000000001}, {u'lat': 37.81848, u'lng': -122.36635000000001}], u'maneuver': u'', u'end_location': {u'lat': 37.818481, u'lng': -122.36635380000001}, u'start_point': {u'lat': 37.8183858, u'lng': -122.36654670000001}, u'instructions': u'Head <b>northeast</b> on <b>Clipper Cove Way</b> toward <b>Avenue G</b>'}, {u'distance': {u'text': u'456 ft', u'value': 139}, u'lat_lngs': [{u'lat': 37.81848, u'lng': -122.36635000000001}, {u'lat': 37.819570000000006, u'lng': -122.36714}], u'travel_mode': u'DRIVING', u'maneuver': u'turn-left', u'end_point': {u'lat': 37.8195713, u'lng': -122.36713659999998}, u'encoded_lat_lngs': u'olyeFttziVyE|C', u'start_location': {u'lat': 37.818481, u'lng': -122.36635380000001}, u'polyline': {u'points': u'olyeFttziVyE|C'}, u'duration': {u'text': u'1 min', u'value': 34}, u'path': [{u'lat': 37.81848, u'lng': -122.36635000000001}, {u'lat': 37.819570000000006, u'lng': -122.36714}], u'end_location': {u'lat': 37.8195713, u'lng': -122.36713659999998}, u'start_point': {u'lat': 37.818481, u'lng': -122.36635380000001}, u'instructions': u'Turn <b>left</b> onto <b>Avenue G</b>'}, {u'distance': {u'text': u'0.3 mi', u'value': 522}, u'lat_lngs': [{u'lat': 37.819570000000006, u'lng': -122.36714}, {u'lat': 37.81947, u'lng': -122.36739000000001}, {u'lat': 37.81942, u'lng': -122.36751000000001}, {u'lat': 37.819140000000004, u'lng': -122.36815000000001}, {u'lat': 37.81891, u'lng': -122.36871000000001}, {u'lat': 37.81875, u'lng': -122.36909000000001}, {u'lat': 37.81841, u'lng': -122.36987}, {u'lat': 37.81819, u'lng': -122.37041}, {u'lat': 37.81801, u'lng': -122.37084000000002}, {u'lat': 37.817820000000005, u'lng': -122.37131000000001}, {u'lat': 37.81758000000001, u'lng': -122.37187000000002}, {u'lat': 37.81752, u'lng': -122.37200000000001}, {u'lat': 37.817400000000006, u'lng': -122.37228}, {u'lat': 37.81736, u'lng': -122.37238}], u'travel_mode': u'DRIVING', u'maneuver': u'turn-left', u'end_point': {u'lat': 37.8173598, u'lng': -122.3723809}, u'encoded_lat_lngs': u'isyeFryziVRp@HVv@~Bl@nB^jAbAzCj@jBb@tAd@|An@nBJXVv@FR', u'start_location': {u'lat': 37.8195713, u'lng': -122.36713659999998}, u'polyline': {u'points': u'isyeFryziVRp@HVv@~Bl@nB^jAbAzCj@jBb@tAd@|An@nBJXVv@FR'}, u'duration': {u'text': u'1 min', u'value': 73}, u'path': [{u'lat': 37.819570000000006, u'lng': -122.36714}, {u'lat': 37.81947, u'lng': -122.36739000000001}, {u'lat': 37.81942, u'lng': -122.36751000000001}, {u'lat': 37.819140000000004, u'lng': -122.36815000000001}, {u'lat': 37.81891, u'lng': -122.36871000000001}, {u'lat': 37.81875, u'lng': -122.36909000000001}, {u'lat': 37.81841, u'lng': -122.36987}, {u'lat': 37.81819, u'lng': -122.37041}, {u'lat': 37.81801, u'lng': -122.37084000000002}, {u'lat': 37.817820000000005, u'lng': -122.37131000000001}, {u'lat': 37.81758000000001, u'lng': -122.37187000000002}, {u'lat': 37.81752, u'lng': -122.37200000000001}, {u'lat': 37.817400000000006, u'lng': -122.37228}, {u'lat': 37.81736, u'lng': -122.37238}], u'end_location': {u'lat': 37.8173598, u'lng': -122.3723809}, u'start_point': {u'lat': 37.8195713, u'lng': -122.36713659999998}, u'instructions': u'Turn <b>left</b> onto <b>California Ave</b>'}, {u'distance': {u'text': u'0.1 mi', u'value': 234}, u'lat_lngs': [{u'lat': 37.81736, u'lng': -122.37238}, {u'lat': 37.817420000000006, u'lng': -122.37250000000002}, {u'lat': 37.81747, u'lng': -122.3726}, {u'lat': 37.8175, u'lng': -122.37264}, {u'lat': 37.81752, u'lng': -122.37267000000001}, {u'lat': 37.81759, u'lng': -122.37273}, {u'lat': 37.817620000000005, u'lng': -122.37279000000001}, {u'lat': 37.817890000000006, u'lng': -122.37298000000001}, {u'lat': 37.81795, u'lng': -122.37303000000001}, {u'lat': 37.81803, u'lng': -122.37307000000001}, {u'lat': 37.81855, u'lng': -122.37342000000001}, {u'lat': 37.81911, u'lng': -122.37379000000001}], u'travel_mode': u'DRIVING', u'maneuver': u'turn-right', u'end_point': {u'lat': 37.81911420000001, u'lng': -122.37379199999998}, u'encoded_lat_lngs': u'oeyeFjz{iVKVIREFCDMJEJu@d@KHOFgBdAoBhA', u'start_location': {u'lat': 37.8173598, u'lng': -122.3723809}, u'polyline': {u'points': u'oeyeFjz{iVKVIREFCDMJEJu@d@KHOFgBdAoBhA'}, u'duration': {u'text': u'1 min', u'value': 34}, u'path': [{u'lat': 37.81736, u'lng': -122.37238}, {u'lat': 37.817420000000006, u'lng': -122.37250000000002}, {u'lat': 37.81747, u'lng': -122.3726}, {u'lat': 37.8175, u'lng': -122.37264}, {u'lat': 37.81752, u'lng': -122.37267000000001}, {u'lat': 37.81759, u'lng': -122.37273}, {u'lat': 37.817620000000005, u'lng': -122.37279000000001}, {u'lat': 37.817890000000006, u'lng': -122.37298000000001}, {u'lat': 37.81795, u'lng': -122.37303000000001}, {u'lat': 37.81803, u'lng': -122.37307000000001}, {u'lat': 37.81855, u'lng': -122.37342000000001}, {u'lat': 37.81911, u'lng': -122.37379000000001}], u'end_location': {u'lat': 37.81911420000001, u'lng': -122.37379199999998}, u'start_point': {u'lat': 37.8173598, u'lng': -122.3723809}, u'instructions': u'Turn <b>right</b> onto <b>Avenue of the Palms</b>'}], u'duration': {u'text': u'2 mins', u'value': 145}, u'end_location': {u'lat': 37.81911420000001, u'lng': -122.37379199999998}}], u'overview_path': [{u'lat': 37.81839, u'lng': -122.36655}, {u'lat': 37.818400000000004, u'lng': -122.36654000000001}, {u'lat': 37.81844, u'lng': -122.36643000000001}, {u'lat': 37.81848, u'lng': -122.36635000000001}, {u'lat': 37.819570000000006, u'lng': -122.36714}, {u'lat': 37.81942, u'lng': -122.36751000000001}, {u'lat': 37.81891, u'lng': -122.36871000000001}, {u'lat': 37.81801, u'lng': -122.37084000000002}, {u'lat': 37.817400000000006, u'lng': -122.37228}, {u'lat': 37.81736, u'lng': -122.37238}, {u'lat': 37.817420000000006, u'lng': -122.37250000000002}, {u'lat': 37.8175, u'lng': -122.37264}, {u'lat': 37.81759, u'lng': -122.37273}, {u'lat': 37.817620000000005, u'lng': -122.37279000000001}, {u'lat': 37.817890000000006, u'lng': -122.37298000000001}, {u'lat': 37.81803, u'lng': -122.37307000000001}, {u'lat': 37.81911, u'lng': -122.37379000000001}]}], u'status': u'OK', u'geocoded_waypoints': [{u'partial_match': True, u'place_id': u'ChIJuQtN5y-AhYAROoYHc3-q9wc', u'geocoder_status': u'OK', u'types': [u'route']}, {u'partial_match': True, u'place_id': u'ChIJezJ6FjSAhYARaBsCYD9lWCE', u'geocoder_status': u'OK', u'types': [u'route']}], u'request': {u'origin': u'Treasure Island Bar & Grill, Clipper Cove Way, San Francisco, CA, United States', u'destination': u'Treasure Island Flea, Avenue of the Palms, San Francisco, CA, United States', u'travelMode': u'DRIVING'}}


class RoadUnitTestCase(unittest.TestCase):

    def test_Route_class_init(self):
        result = road.Route(DIRECTIONS_RESULT, "03:01", "tomorrow")

        # Check that it's an instance of a Route object.
        self.assertIsInstance(result, road.Route)

        # Check that it has the correct number of steps.
        self.assertEqual(len(result.steps), 4)

        # Check that it has the correct overall duration.
        self.assertEqual(result.overall_duration, 145)

        # Check the initial values for time_in_bucket, time_elapsed, and size_of_bucket.
        self.assertEqual(result.time_in_bucket, 0)
        self.assertEqual(result.time_elapsed, 0)
        self.assertEqual(result.size_of_bucket, 900)

        # Check that starting location coords are in coords_time.
        self.assertIn((37.8183858, -122.36654670000001), result.coords_time[0])

        # Check that departure_day (``tomorrow``) has been set correctly.
        self.assertTrue(result.start_time.is_tomorrow())

    def test_Route_class_make_coords_time(self):
        result = road.Route(DIRECTIONS_RESULT, "03:01", "tomorrow").make_coords_time()
        print result

        self.assertEqual(len(result), 3)


    def test_format_time(self):
        result = road.format_time((40.712784, -74.005941), "03:01")

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

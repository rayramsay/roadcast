import unittest
import pendulum

import road

# FIXME: Put DIRECTIONS_RESULT into setup.
# FIXME: Mock weather API results (dictionary with lat/lngs and weathers) so that it gets back wrong weather if it looks in wrong place.

DIRECTIONS_RESULT_899 = {u'routes': [{u'legs': [{u'duration': {u'value': 899}, u'start_location': {u'lat': 1, u'lng': 100}, u'end_location': {u'lat': 1, u'lng': 129}, u'steps': [{u'duration': {u'value': 400}, u'start_location': {u'lat': 1, u'lng': 100}, u'end_location': {u'lat': 1, u'lng': 110}, u'path': [{u'lat': 1, u'lng': 100}, {u'lat': 1, u'lng': 101}, {u'lat': 1, u'lng': 102}, {u'lat': 1, u'lng': 103}, {u'lat': 1, u'lng': 104}, {u'lat': 1, u'lng': 105}, {u'lat': 1, u'lng': 106}, {u'lat': 1, u'lng': 107}, {u'lat': 1, u'lng': 108}, {u'lat': 1, u'lng': 109}, {u'lat': 1, u'lng': 110}]}, {u'duration': {u'value': 300}, u'start_location': {u'lat': 1, u'lng': 110}, u'end_location': {u'lat': 1, u'lng': 120}, u'path': [{u'lat': 1, u'lng': 110}, {u'lat': 1, u'lng': 111}, {u'lat': 1, u'lng': 112}, {u'lat': 1, u'lng': 113}, {u'lat': 1, u'lng': 114}, {u'lat': 1, u'lng': 115}, {u'lat': 1, u'lng': 116}, {u'lat': 1, u'lng': 117}, {u'lat': 1, u'lng': 118}, {u'lat': 1, u'lng': 119}, {u'lat': 1, u'lng': 120}]}, {u'duration': {u'value': 199}, u'start_location': {u'lat': 1, u'lng': 120}, u'end_location': {u'lat': 1, u'lng': 129}, u'path': [{u'lat': 1, u'lng': 120}, {u'lat': 1, u'lng': 121}, {u'lat': 1, u'lng': 122}, {u'lat': 1, u'lng': 123}, {u'lat': 1, u'lng': 124}, {u'lat': 1, u'lng': 125}, {u'lat': 1, u'lng': 126}, {u'lat': 1, u'lng': 127}, {u'lat': 1, u'lng': 128}, {u'lat': 1, u'lng': 129}]}]}]}]}
DIRECTIONS_RESULT_1999 = {u'routes': [{u'legs': [{u'duration': {u'value': 1999}, u'start_location': {u'lat': 1, u'lng': 100}, u'end_location': {u'lat': 1, u'lng': 129}, u'steps': [{u'duration': {u'value': 800}, u'start_location': {u'lat': 1, u'lng': 100}, u'end_location': {u'lat': 1, u'lng': 110}, u'path': [{u'lat': 1, u'lng': 100}, {u'lat': 1, u'lng': 101}, {u'lat': 1, u'lng': 102}, {u'lat': 1, u'lng': 103}, {u'lat': 1, u'lng': 104}, {u'lat': 1, u'lng': 105}, {u'lat': 1, u'lng': 106}, {u'lat': 1, u'lng': 107}, {u'lat': 1, u'lng': 108}, {u'lat': 1, u'lng': 109}, {u'lat': 1, u'lng': 110}]}, {u'duration': {u'value': 1000}, u'start_location': {u'lat': 1, u'lng': 110}, u'end_location': {u'lat': 1, u'lng': 120}, u'path': [{u'lat': 1, u'lng': 110}, {u'lat': 1, u'lng': 111}, {u'lat': 1, u'lng': 112}, {u'lat': 1, u'lng': 113}, {u'lat': 1, u'lng': 114}, {u'lat': 1, u'lng': 115}, {u'lat': 1, u'lng': 116}, {u'lat': 1, u'lng': 117}, {u'lat': 1, u'lng': 118}, {u'lat': 1, u'lng': 119}, {u'lat': 1, u'lng': 120}]}, {u'duration': {u'value': 199}, u'start_location': {u'lat': 1, u'lng': 120}, u'end_location': {u'lat': 1, u'lng': 129}, u'path': [{u'lat': 1, u'lng': 120}, {u'lat': 1, u'lng': 121}, {u'lat': 1, u'lng': 122}, {u'lat': 1, u'lng': 123}, {u'lat': 1, u'lng': 124}, {u'lat': 1, u'lng': 125}, {u'lat': 1, u'lng': 126}, {u'lat': 1, u'lng': 127}, {u'lat': 1, u'lng': 128}, {u'lat': 1, u'lng': 129}]}]}]}]}


class APITranslationTestCase(unittest.TestCase):

    def test_prep_directions(self):
        result = road.prep_directions(DIRECTIONS_RESULT_899)

        # Check that it returns a dictionary.
        self.assertIs(type(result), dict)

        # Check that it has the keys it should.
        self.assertTrue("steps" in result)
        self.assertTrue("duration" in result)

        # Check that it has the right number of steps.
        self.assertEqual(len(result["steps"]), 3)

        # Check that the duration is an integer.
        self.assertIs(type(result["duration"]), int)

    def test_prep_weather(self):
        #FIXME: Write prep weather tests.
        pass

################################################################################

if __name__ == '__main__':
    unittest.main()

import unittest
import pendulum

import road


class RoadUnitTestCase(unittest.TestCase):

    def test_format_time(self):
        result = road.format_time((40.712784, -74.005941), "03:01")

        # Check that it's a Pendulum object.
        self.assertIsInstance(result, pendulum.pendulum.Pendulum)

        # Check that the date is today.
        self.assertTrue(result.is_same_day(pendulum.now()))

        # Check that it has the correct timezone.
        self.assertTrue(result.timezone_name, 'America/New_York')

        # Check that it has the right hour and minutes.
        self.assertTrue(result.hour, 3)
        self.assertTrue(result.minute, 1)

if __name__ == '__main__':
    unittest.main()

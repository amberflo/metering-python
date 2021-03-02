from datetime import datetime
import unittest

from dateutil.tz import tzutc

from metering import utils


class TestUtils(unittest.TestCase):

    def test_timezone_utils(self):
        now = datetime.now()
        utcnow = datetime.now(tz=tzutc())
        self.assertTrue(utils.is_naive(now))
        self.assertFalse(utils.is_naive(utcnow))

        fixed = utils.guess_timezone(now)
        self.assertFalse(utils.is_naive(fixed))

        shouldnt_be_edited = utils.guess_timezone(utcnow)
        self.assertEqual(utcnow, shouldnt_be_edited)

if __name__ == '__main__':
    unittest.main()

"""
Run like so:
    $ python3 tests.py
"""

import datetime
import unittest

from instrument import Instrument
from oanda import Oanda

class TestDaemon(unittest.TestCase):

    def setUp(self):
        # called for every test method
        pass


    def tearDown(self):
        # called for every test method
        pass
    

    def test_get_time_until_close (self):
        zero_delta = datetime.timedelta()
        result = Oanda.get_time_until_close() # timedelta
        api_open = Oanda.is_market_open(Instrument(4))
        if api_open:
            self.assertTrue(result != zero_delta)
        else:
            self.assertTrue(result == zero_delta)
        print('*****************************************')
        print('time until market close: {}    *****'.format(result))
        print('*****************************************')
        

    def test_get_time_since_close (self):
        """
        Constraints: # TODO: make more precise
            - less than one week ago
            - before now
            - if market open now, > 2 days ago
            - if market closed now, less than 2 days ago
        """
        now = datetime.datetime.utcnow()
        zero_delta = datetime.timedelta()
        time_since_close = Oanda.get_time_since_close() # timedelta
        # check < 1 week
        self.assertTrue(now - (now - time_since_close) < datetime.timedelta(days=7))
        # Check before now
        self.assertTrue((now - time_since_close) < now)
        # Check weekend (2 days)
        api_open = Oanda.is_market_open(Instrument(4))
        if api_open:
            self.assertTrue(now - (now - time_since_close) > datetime.timedelta(days=2))
        else:
            self.assertTrue(now - (now - time_since_close) < datetime.timedelta(days=2))
        print('***********************************************\\')
        print('time since last close: {}'.format(time_since_close))
        print('***********************************************/')


if __name__ == '__main__':
    unittest.main()


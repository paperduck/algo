"""
Run like so:
    $ python3 tests.py
"""

import datetime
import unittest

from config import Config
from instrument import Instrument
from oanda import Oanda

class TestDaemon(unittest.TestCase):

    def setUp(self):
        # called for every test method
        pass


    def tearDown(self):
        # called for every test method
        pass
    

    def test_get_auth_key(self):
        result = None
        result = Oanda.get_auth_key()
        self.assertTrue(result) # not None


    def test_fetch(self):
        result = None
        result = Oanda.fetch( '{}/v3/accounts'.format(Config.oanda_url) )
        self.assertTrue(result) # not None
        result = Oanda.fetch( '{}/v3/xxxxxx'.format(Config.oanda_url) )
        self.assertEqual(result, None) # None


    def test_get_prices(self):
        result = None
        result = Oanda.get_prices( [Instrument(4)] )
        self.assertTrue(result) # not None


    def test_get_time_until_close (self):
        zero_delta = datetime.timedelta()
        result = Oanda.get_time_until_close() # timedelta
        api_open = Oanda.is_market_open(Instrument(4))
        if api_open:
            self.assertTrue(result != zero_delta)
        else:
            self.assertTrue(result == zero_delta)
        print('*****************************************\\')
        print('time until market close: {}'.format(result))
        print('*****************************************/')
        

    def test_get_time_since_close (self):
        """
        These should be true of the time since close:
            - less than one week ago
            - before now
            - if market open now, > 2 days ago
            - if market closed now, less than 2 days ago
        """
        now = datetime.datetime.utcnow()
        zero_delta = datetime.timedelta()
        time_since_close = Oanda.get_time_since_close() # timedelta
        print('***********************************************\\')
        print('time since last close: {}'.format(time_since_close))
        print('***********************************************/')
        # check < 1 week
        self.assertTrue(now - (now - time_since_close) < datetime.timedelta(days=7))
        # Check before now
        self.assertTrue((now - time_since_close) < now)
        # Check weekend (2 days)
        market_open = Oanda.is_market_open(Instrument(4)) # USD/JPY market
        if market_open:
            self.assertTrue( time_since_close > datetime.timedelta(days=2))
        else:
            self.assertTrue( time_since_close < datetime.timedelta(days=2))


if __name__ == '__main__':
    unittest.main()


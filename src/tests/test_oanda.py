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
        

if __name__ == '__main__':
    unittest.main()


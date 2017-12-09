"""
Test the chart.py module.
"""

# library imports
import datetime
import sys
import unittest
from unittest.mock import MagicMock, patch, call

# Need to modify sys.path because Python doesn't have relative imports.
# sys.path is initialized from environment variable PYTHONPATH.
try:
    sys.path.index('/home/user/raid/software_projects/algo/src')
except ValueError:
    sys.path.append('/home/user/raid/software_projects/algo/src')

# local imports
from chart import Chart
#from config import Config
from db import DB
from instrument import Instrument

class TestChart(unittest.TestCase):


    # called for every test method
    def setUp(self):
        pass

    # called for every test method
    def tearDown(self):
        # TODO rework DB because this is annoying
        DB.shutdown()

    
    """
    """
    def test___init__(self):
        """
        count, no start, no end
        """
        COUNT = 100
        sample_instrument = Instrument(4) # USD_JPY
        chart = Chart(in_instrument=sample_instrument, count=COUNT)
        # check success
        self.assertNotEqual(chart._granularity, None)
        # check indecies
        self.assertTrue(
            chart._start_index == chart._end_index + 1
            or (chart._start_index == 0 and chart._end_index == COUNT - 1)
        )
        # check instrument
        self.assertEqual(sample_instrument.get_id(), chart._instrument.get_id())
        self.assertEqual(sample_instrument.get_name(), chart._instrument.get_name())
        # check granularity
        self.assertEqual(chart._granularity, 'S5') # Oanda's default
        # check count
        self.assertEqual(chart.get_size(), COUNT)
        # check start time - should be within (granularity * COUNT) before now.
        # Allow some extra time for the REST call.
        num_extra_seconds = 3
        max_timedelta = datetime.timedelta(seconds=(5 * COUNT + num_extra_seconds))

        print('start to now: {}'.format(
            datetime.datetime.utcnow() - chart.get_start_timestamp()
        ))
        return

        self.assertTrue(datetime.datetime.utcnow() - chart.get_start_timestamp()
            <= max_timedelta)
        # check end time - should be very recent
        max_timedelta = datetime.timedelta(seconds=num_extra_seconds)
        #import pdb; pdb.set_trace()

        print('end to now: {}'.format(
            datetime.datetime.utcnow() - chart.get_end_timestamp()
        ))

        self.assertTrue(datetime.datetime.utcnow() - chart.get_end_timestamp()
            < max_timedelta)
        # check candle format
        self.assertEqual(chart._candle_format, 'bidask') # Oanda's default
        


if __name__ == '__main__':
    unittest.main()

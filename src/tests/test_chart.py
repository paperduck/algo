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
from broker import Broker
from chart import Chart
#from config import Config
from db import DB
from instrument import Instrument
import util_date

class TestChart(unittest.TestCase):


    # called for every test method
    def setUp(self):
        pass


    # called for every test method
    def tearDown(self):
        pass

    
    """
    """
    def test___init__(self):
        return ###########################################################################################
        """
        Case:     count, no start, no end
        """
        COUNT = 100
        GRANULARITY = 'S5'
        NUM_EXTRA_SECONDS = 300
        sample_instrument = Instrument(4) # USD_JPY

        # Initialize a sample chart.
        chart = Chart(
            in_instrument=sample_instrument,
            count=COUNT
        )

        # check success
        self.assertNotEqual(chart._granularity, None)
        # check indecies
        self.assertTrue(
            chart._start_index == 0 and chart._end_index == COUNT - 1
        )
        # check instrument
        self.assertEqual(sample_instrument.get_id(), chart._instrument.get_id())
        self.assertEqual(sample_instrument.get_name(), chart._instrument.get_name())
        # check granularity
        self.assertEqual(chart._granularity, GRANULARITY) # Oanda's default (S5)
        # check count
        self.assertEqual(chart.get_size(), COUNT)

        # check candle format
        # If 'bidask', then the midpoints will be None, and vice-versa
        self.assertNotEqual(chart[0].open_bid, None) # Oanda's default

        start = None
        chart = None
        

        """
        Case:     count, start, no end
        """
        COUNT = 100
        GRANULARITY = 'M1'
        sample_instrument = Instrument(4) # USD_JPY

        # Initialize a sample chart with no market close gaps.
        # start = now + time until close - 1 week - chart size
        # add wiggle room before market close for skipped candles
        start = datetime.datetime.utcnow() \
            + Broker.get_time_until_close() \
            - datetime.timedelta(days=7) \
            - datetime.timedelta(minutes = COUNT + 60)
        chart = Chart(
            in_instrument=sample_instrument,
            count=COUNT,
            start=start,
            granularity=GRANULARITY
        )

        # check success
        self.assertNotEqual(chart._granularity, None)
        # check indecies
        self.assertTrue(
            chart._start_index == 0 and chart._end_index == COUNT - 1
        )
        # check instrument
        self.assertEqual(sample_instrument.get_id(), chart._instrument.get_id())
        self.assertEqual(sample_instrument.get_name(), chart._instrument.get_name())
        # check granularity
        self.assertEqual(chart._granularity, GRANULARITY)
        # check count
        self.assertEqual(chart.get_size(), COUNT)

        # check start time
        if Broker.get_time_until_close() == datetime.timedelta():
            # market closed, so there will be a significat gap
            # TODO: make this more precise. 3 Day wiggle room not good.
            self.assertTrue(
                abs(start - chart.get_start_timestamp()) < datetime.timedelta(days=3)
            )
        else:
            self.assertTrue(
                # Candles gap if there were no ticks, so allow some wiggle room.
                abs(start - chart.get_start_timestamp()) < datetime.timedelta(minutes=5)
            )
        # check end time
        end_expected = datetime.datetime.utcnow() \
                + Broker.get_time_until_close() \
                - datetime.timedelta(days=7)
        end_real = chart.get_end_timestamp()
        if Broker.get_time_until_close() == datetime.timedelta():
            self.assertTrue(
                abs(end_expected - end_real) < datetime.timedelta(days=3)
            )
        else:
            self.assertTrue(
                # Candles gap if there were no ticks, so allow some wiggle room.
                abs(end_expected - end_real) < datetime.timedelta(hours=1)
            )
        # check candle format
        # If 'bidask', then the midpoints will be None, and vice-versa
        self.assertNotEqual(chart[0].open_bid, None) # Oanda's default


        """
        count, no start, end
        """
        COUNT = 100
        GRANULARITY = 'H2'

        sample_instrument = Instrument(4) # USD_JPY

        # Initialize a sample chart.
        chart = Chart(
            in_instrument=sample_instrument,
            count=COUNT,
            end=datetime.datetime.utcnow(),
            granularity=GRANULARITY
        )

        # check success
        self.assertNotEqual(chart._granularity, None)
        # check indecies
        self.assertTrue(
            chart._start_index == 0 and chart._end_index == COUNT - 1
        )
        # check instrument
        self.assertEqual(sample_instrument.get_id(), chart._instrument.get_id())
        self.assertEqual(sample_instrument.get_name(), chart._instrument.get_name())
        # check granularity
        self.assertEqual(chart._granularity, GRANULARITY)
        # check count
        self.assertEqual(chart.get_size(), COUNT)

        # check start time
        """self.assertTrue(
            # Candles gap if there were no ticks, so allow some wiggle room.
            abs(start - chart.get_start_timestamp()) < datetime.timedelta(minutes=5)
        )"""
        # check end time
        end_expected = datetime.datetime.utcnow()
        end_real = chart.get_end_timestamp()
        #print('3. end_expected - end_real = {}'.format(end_expected - end_real))
        if Broker.get_time_until_close() == datetime.timedelta():
            self.assertTrue(
                abs(end_expected - end_real) < datetime.timedelta(days=3)
            )
        else:
            self.assertTrue(
                # Candles gap if there were no ticks, so allow some wiggle room.
                abs(end_expected - end_real) < datetime.timedelta(hours=5)
            )
        # check candle format
        # If 'bidask', then the midpoints will be None, and vice-versa
        self.assertNotEqual(chart[0].open_bid, None) # Oanda's default


        """
        no count, start, no end
        """
        COUNT = 24
        GRANULARITY = 'M' # month (Oanda)
        sample_instrument = Instrument(4) # USD_JPY

        # Initialize a sample chart.
        # start = now - 2 years
        start = datetime.datetime.utcnow() - datetime.timedelta(days=365*2)
        chart = Chart(
            in_instrument=sample_instrument,
            start=start,
            granularity=GRANULARITY
        )

        # check success
        self.assertNotEqual(chart._granularity, None)
        # check indecies
        self.assertTrue(
            chart._start_index == 0 and abs(chart._end_index - COUNT) <= 1
        )
        # check instrument
        self.assertEqual(sample_instrument.get_id(), chart._instrument.get_id())
        self.assertEqual(sample_instrument.get_name(), chart._instrument.get_name())
        # check granularity
        self.assertEqual(chart._granularity, GRANULARITY)
        # check count
        print('{} ~= {}'.format(chart.get_size(), COUNT))
        self.assertTrue(
            abs(chart.get_size() - COUNT) <= 1
        )

        # check start time
        self.assertTrue(
            # allow wiggle room.
            abs(start - chart.get_start_timestamp()) < datetime.timedelta(days=32)
        )
        # check end time
        end_expected = datetime.datetime.utcnow()
        end_real = chart.get_end_timestamp()
        #print('4. end_expected - end_real = {}'.format(end_expected - end_real))
        self.assertTrue(
            # Allow wiggle room for market close.
            abs(end_expected - end_real) < datetime.timedelta(days=32)
        )
        # check candle format
        # If 'bidask', then the midpoints will be None, and vice-versa
        self.assertNotEqual(chart[0].open_bid, None) # Oanda's default


    """
    test: Chart.update()
    Constraints to verify:
        - Data is as recent as possible
        - start index has earliest timestamp
        - end index has latest timestamp
        - timestamps from start to end are sequential
    Situations:
        - old chart (complete update)
        - somewhat outdated chart (partially updated)
        - new chart (no updates other than last (incomplete) candle)
    """
    def test_update(self):
        """
        old chart that gets completely updated
        """
        # initial "outdated" chart
        chart = Chart(
            in_instrument=Instrument(4),
            granularity='M1',
            count=300,
            end=datetime.datetime(year=2017, month=12, day=5)
        )
        # Update chart
        chart.update()

        # Verify data is most recent
        time_since_close = Broker.get_time_since_close()
        now = datetime.datetime.utcnow()
        end_timestamp = chart.get_end_timestamp()       
        if (Broker.get_time_until_close() == datetime.timedelta()):
            # market closed now, so incorporate delay
            print( 'time since end_timestamp: {}'.format(now - end_timestamp) ) 
            print( 'time_since_close: {}'.format(time_since_close) ) 
            self.assertTrue(abs((now - end_timestamp) - (time_since_close)) < datetime.timedelta(minutes=2))
        else:
            self.assertTrue(abs(now - end_timestamp) < datetime.timedelta(minutes=2))

        # verify candle at start index has earliest timestamp.
        earliest_timestamp = datetime.datetime.utcnow()
        for i in range(0, chart.get_size()):
            if chart[i].timestamp < earliest_timestamp:
                earliest_timestamp = chart[i].timestamp
        self.assertTrue(chart.get_start_timestamp() == earliest_timestamp)
        # verify candle at end index has latest timestamp.
        latest_timestamp = datetime.datetime(year=1999, month=1, day=1)
        for i in range(0, chart.get_size()):
            if chart[i].timestamp > latest_timestamp:
                latest_timestamp = chart[i].timestamp
        self.assertTrue(chart.get_end_timestamp() == latest_timestamp)
        # Verify sequential timestamps
        for i in range(0, chart.get_size() - 1):
            self.assertTrue(chart[i].timestamp < chart[i + 1].timestamp)
        """
        Chart that gets partially updated
        """
        # TODO
        """
        Chart that gets barely updated
        """
        # TODO


if __name__ == '__main__':
    unittest.main()

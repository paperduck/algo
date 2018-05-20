"""
Test the chart.py module.
"""

# library imports
from datetime import datetime, timedelta
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
from candle import Candle
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
            chart._start_index == 0 and chart._get_end_index() == COUNT - 1
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
        WIGGLE_MINUTES = 5 # no price change -> no candle
        ADJUSTMENT = 120
        sample_instrument = Instrument(4) # USD_JPY

        # Initialize a sample chart with no market close gaps.
        # start = now - time since close - chart size 
        #   - (adjustment to busy time to avoid gaps) - skipped candle slack
        start = datetime.utcnow() \
            - Broker.get_time_since_close() \
            - timedelta(minutes = COUNT + ADJUSTMENT + WIGGLE_MINUTES)
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
            chart._start_index == 0 and chart._get_end_index() == COUNT - 1
        )
        # check instrument
        self.assertEqual(sample_instrument.get_id(), chart._instrument.get_id())
        self.assertEqual(sample_instrument.get_name(), chart._instrument.get_name())
        # check granularity
        self.assertEqual(chart._granularity, GRANULARITY)
        # check count
        self.assertEqual(chart.get_size(), COUNT)
        # check start time
        self.assertTrue(
            # Candles gap if there were no ticks, so allow some wiggle room.
            abs(start - chart.get_start_timestamp()) < timedelta(minutes=WIGGLE_MINUTES)
        )
        # check end time
        end_expected = start + timedelta(minutes=COUNT)
        end_real = chart.get_end_timestamp()
        self.assertTrue(
            # Candles gap if there were no ticks, so allow some wiggle room.
            abs(end_expected - end_real) < timedelta(minutes=WIGGLE_MINUTES)
        )
        # check candle format
        self.assertNotEqual(chart[0].open_bid, None)


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
            end=datetime.utcnow(),
            granularity=GRANULARITY
        )

        # check success
        self.assertNotEqual(chart._granularity, None)
        # check indecies
        self.assertTrue(
            chart._start_index == 0 and chart._get_end_index() == COUNT - 1
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
            abs(start - chart.get_start_timestamp()) < timedelta(minutes=5)
        )"""
        # check end time
        end_expected = datetime.utcnow()
        end_real = chart.get_end_timestamp()
        if Broker.get_time_until_close() == timedelta():
            self.assertTrue(
                abs(end_expected - end_real) < timedelta(days=3)
            )
        else:
            self.assertTrue(
                # Candles gap if there were no ticks, so allow some wiggle room.
                abs(end_expected - end_real) < timedelta(hours=5)
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
        start = datetime.utcnow() - timedelta(days=365*2)
        chart = Chart(
            in_instrument=sample_instrument,
            start=start,
            granularity=GRANULARITY
        )

        # check success
        self.assertNotEqual(chart._granularity, None)
        # check indecies
        self.assertTrue(
            chart._start_index == 0 and abs(chart._get_end_index() - COUNT) <= 1
        )
        # check instrument
        self.assertEqual(sample_instrument.get_id(), chart._instrument.get_id())
        self.assertEqual(sample_instrument.get_name(), chart._instrument.get_name())
        # check granularity
        self.assertEqual(chart._granularity, GRANULARITY)
        # check count
        self.assertTrue( abs(chart.get_size() - COUNT) <= 1 )

        # check start time
        self.assertTrue(
            # allow wiggle room.
            abs(start - chart.get_start_timestamp()) < timedelta(days=32)
        )
        # check end time
        end_expected = datetime.utcnow()
        end_real = chart.get_end_timestamp()
        self.assertTrue(
            # Allow wiggle room for market close.
            abs(end_expected - end_real) < timedelta(days=32)
        )
        # check candle format
        # If 'bidask', then the midpoints will be None, and vice-versa
        self.assertNotEqual(chart[0].open_bid, None) # Oanda's default


    def test_update(self):
        """
        test: Chart.update()
        Constraints to verify:
            - Data is as recent as possible
            - start index has earliest timestamp
            - end index has latest timestamp
            - timestamps from start to end are sequential
        Cases:
            - old chart (complete update)
            - somewhat outdated chart (partially updated)
            - new chart (no updates other than last (incomplete) candle)
        """

        """
        case: old chart that gets completely updated
        """
        # initial "outdated" chart
        chart = Chart(
            in_instrument=Instrument(4),
            granularity='M1',
            count=4999,
            end=datetime(year=2017, month=12, day=5)
        )
        # Update chart
        chart.update()

        # Verify data is most recent
        time_since_close = Broker.get_time_since_close()
        now = datetime.utcnow()
        end_timestamp = chart.get_end_timestamp()       
        if (Broker.get_time_until_close() == timedelta()):
            # Time since last candle should be close to time since market
            # close. The leniency is high to allow for periods of no new
            # candles.
            self.assertTrue(
                abs((now - end_timestamp) - (time_since_close))
                     < timedelta(minutes=62)
            )
        else:
            # Time since last candle should be close to now.
            self.assertTrue(abs(now - end_timestamp) < timedelta(minutes=2))
        # verify candle at start index has earliest timestamp.
        earliest_timestamp = datetime.utcnow()
        for i in range(0, chart.get_size()):
            if chart[i].timestamp < earliest_timestamp:
                earliest_timestamp = chart[i].timestamp
        self.assertTrue(chart.get_start_timestamp() == earliest_timestamp)
        # verify candle at end index has latest timestamp.
        latest_timestamp = datetime(year=1999, month=1, day=1)
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


    def test_pearson(self):
        """
        case: empty chart
        """
        c = Chart( Instrument(4) )
        self.assertRaises(Exception, c.pearson, 0, c.get_size() )

        """
        case: one candle
        """
        # TODO

        """
        case: straight line
        """
        c = Chart(
            in_instrument=Instrument(4),
            count=0
        )
        fake_candles = []
        fake_timestamp = datetime.utcnow()
        fake_price = 100.1234
        for i in range(0,10):
            fake_candles.append( Candle(
                timestamp=fake_timestamp + timedelta(seconds=i),   
                high_ask=fake_price + i,
                low_bid=(fake_price + i / 2)
            ) )
        c._candles = fake_candles
        pearson = c.pearson( 0, c.get_size() - 1, 'high_low_avg' )
        self.assertEqual( pearson, 1 )
    

if __name__ == '__main__':
    unittest.main()

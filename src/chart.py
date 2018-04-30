
# library imports
#import array
import datetime

# local imports
from broker import Broker
from candle import Candle
from instrument import Instrument
from log import Log
import util_date
import utils

"""
A <Chart> is a group of sequential <Candle>s.
"""
class Chart:
    
    """
    Return type: void
    Basically just forward the arguments to the broker API,
        then gather the returned candlesticks.
    """
    def __init__(
        self,
        in_instrument,              # <Instrument>    
        granularity=None,           # string - See Oanda's documentation
        count=None,                 # int - number of candles
        start=None,                 # datetime - UTC
        end=None,                   # datetime - UTC
        price='MBA',                # string
        include_first=None,         # bool
        daily_alignment=None,       # int
        alignment_timezone=None,    # string - timezone
        weekly_alignment=None
    ):
        self._candles = []
        # verify instance of <Instrument> by accessing a member.
        if in_instrument.get_id() == 0:
            pass            
        # get candles from broker
        instrument_history = Broker.get_instrument_history(
            instrument=in_instrument,
            granularity=granularity,
            count=count,
            from_time=start,
            to=end,
            price=price,
            include_first=include_first,
            daily_alignment=daily_alignment,
            alignment_timezone=alignment_timezone,
            weekly_alignment=weekly_alignment
        )
        if instrument_history == None:
            Log.write('chart.py __init__(): Failed to get instrument history.')
            raise Exception
        else:
            candles_raw = instrument_history['candles']
            for c_r in candles_raw:
                new_candle = Candle(
                    timestamp=util_date.string_to_date(c_r['time']),
                    volume=float(c_r['volume']),
                    complete=bool(c_r['complete']),
                    open_bid=float(c_r['bid']['o']),
                    high_bid=float(c_r['bid']['h']),
                    low_bid=float(c_r['bid']['l']),
                    close_bid=float(c_r['bid']['c']),
                    open_ask=float(c_r['ask']['o']),
                    high_ask=float(c_r['ask']['h']),
                    low_ask=float(c_r['ask']['l']),
                    close_ask=float(c_r['ask']['c'])
                )
                self._candles.append(new_candle)

        self._instrument = in_instrument
        self._granularity = instrument_history['granularity']
        self._start_index = 0 # start
        self._price = price
        self.include_first = include_first
        self.daily_alignment = daily_alignment
        self._alignment_timezone = alignment_timezone
        self.weekly_alignment = weekly_alignment


    def __str__(self):
        return "Chart"


    def _get_end_index(self):
        if self._start_index > 0:
            return self._start_index - 1
        elif self._start_index == 0:
            return self.get_size() - 1
        else:
            raise Exception


    def get_size(self):
        """Return type: int
        Returns: Number of candles in chart.
        https://wiki.python.org/moin/TimeComplexity
        len(<list>) in Python is O(1), so no need to store size.
        """
        return len(self._candles)


    def get_instrument(self):
        """Return type: <Instrument> instance
        """
        return self._instrument


    """
    Return type: string (See Oanda's documentation)
    """
    def get_granularity(self):
        return self._granularity


    """
    Return type: datetime
    """
    def get_start_timestamp(self):
        return self._candles[self._start_index].timestamp


    def get_end_timestamp(self):
        """Return type: datetime
        Return the time and date of the last candlestick.
        """
        return self._candles[self._get_end_index()].timestamp


    def get_time_span(self):
        """Return type: datetime.timedelta
        Get time difference between first and last candles.
        """
        return self.get_end_timestamp() - self.get_start_timestamp()


    def get_lag(self):
        """Return type: datetime.timedelta
        Returns time difference between the last candlestick and now.
        """
        return datetime.datetime.utcnow() - self.get_end_timestamp()


    def _increment_start_index(self):
        if self._start_index < self.get_size() - 1:
            self._start_index += 1
        elif self._start_index == self.get_size() - 1:
            self._start_index = 0
        else:
            raise Exception


    def set(self, start_time):
        """Return type: None on failure, 0 on success
        Basically re-initialize the chart.
        Use this for storing candles from a particular point in time.
        Use update() to get the latest candles.
        """
        raise NotImplementedError


    def update(self):
        """Returns: void
        Replace the candles with the most recent ones available.
        Algorithm for minimizing number of updated candles:
            Get the time difference from chart end to now.
            If the time difference is greater than the width of the chart,
                request <chart size> candles.
            else,
                request candles from end of chart to now.
        """
        new_history = None
        if self.get_lag() > self.get_time_span():
            # replace all candles
            new_history = Broker.get_instrument_history(
                instrument=self._instrument,
                granularity=self._granularity,
                count=self.get_size(), 
                to=datetime.datetime.utcnow()
            )
        else:
            # request new candles starting from end of chart
            # TODO verify candleFormat is same as existing chart
            new_history_ = broker.get_instrument_history(
                instrument=self._instrument,
                granularity=self._granularity,
                from_time=self.get_end_timestamp
            )
        if new_history == None:
            Log.write('chart.py update(): Failed to get new candles.')
            raise Exception
        else:
            # Got new candles. Stow them.
            new_candles = new_history['candles']
            # Iterate forwards from last candle. The last candle is probably
            # non-complete, so overwrite it. This thereby fills in the missing
            # gap between (end of chart) and (now). If the gap is smaller 
            # than the size of the chart, only the beginning of the chart is
            # overwritten. If the gap is bigger than the chart, all candles
            # get overwritten. 
            for i in range(0, len(self._candles)):
                # TODO assuming bid/ask candles
                new_candle = new_candles[i]
                self._candles[self._get_end_index()].timestamp    = util_date.string_to_date(new_candle['time'])
                self._candles[self._get_end_index()].volume       = float(new_candle['volume'])
                self._candles[self._get_end_index()].complete     = bool(new_candle['complete'])
                self._candles[self._get_end_index()].open_bid     = float(new_candle['bid']['o'])
                self._candles[self._get_end_index()].open_ask     = float(new_candle['ask']['o'])
                self._candles[self._get_end_index()].high_bid     = float(new_candle['bid']['h'])
                self._candles[self._get_end_index()].high_ask     = float(new_candle['ask']['h'])
                self._candles[self._get_end_index()].low_bid      = float(new_candle['bid']['l'])
                self._candles[self._get_end_index()].low_ask      = float(new_candle['ask']['l'])
                self._candles[self._get_end_index()].close_bid    = float(new_candle['bid']['c'])
                self._candles[self._get_end_index()].close_ask    = float(new_candle['ask']['c'])
                if i < len(self._candles) - 1:
                    self._increment_start_index() # increments end index too


    """
    Return type: <Candle>
    This makes the class accessable using the [] operator.
    """
    def __getitem__(
        self,
        key     # int
    ):
        if key < 0 or key >= len(self._candles):
            raise Exception
        return self._candles[(key + self._start_index) % len(self._candles)]


    """
    Makes the class settable via the [] operator.
    There is probably no reason to implement this.
    """
    def __setitem__(self, key, value):
        raise NotImplementedError


    """
    Return type: float
    end         int     End index of slice. Defaults to chart end.
    """
    def standard_deviation(self,
        start=None, # candle index - default to first
        end=None    # candle index - default to last
    ):
        raise NotImplementedError


    """
    Return type: probably float in a certain range
    """
    def linearity(
        self,
        start=None,     # candle index - default to first
        end=None        # candle index - default to last
    ):
        # pearson coefficient
        raise NotImplementedError


    """
    """
    def slope(self, something):
        # "simple linear regression" or just two point slope
        raise NotImplementedError


    """
    not really sure
    """    
    def noise(self,
        start=None,     # candle index - default to first
        end=None        # candle index - default to last
    ):
        raise NotImplementedError
    

    """        
    # Anscombe's quartet
    """


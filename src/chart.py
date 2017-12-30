
# library imports
import array

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
        candle_format=None,         # string - See Oanda's documentation
        include_first=None,
        daily_alignment=None,
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
            start=start,
            end=end,
            candle_format=candle_format,
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
                    open_bid=float(c_r['openBid']),
                    open_ask=float(c_r['openAsk']),
                    high_bid=float(c_r['highBid']),
                    high_ask=float(c_r['highAsk']),
                    low_bid=float(c_r['lowBid']),
                    low_ask=float(c_r['lowAsk'])
                )
                self._candles.append(new_candle)

        self._instrument = in_instrument
        self._granularity = instrument_history['granularity']
        self._start_index = 0           
        self._end_index = len(self._candles) - 1
        self._candle_format = candle_format
        self.include_first = include_first
        self.daily_alignment = daily_alignment
        self._alignment_timezone = alignment_timezone
        self.weekly_alignment = weekly_alignment


    """
    """
    def __str__(self):
        return "Chart"


    """
    Return type: int
    Returns: Number of candles in chart.
    https://wiki.python.org/moin/TimeComplexity
    len(<list>) in Python is O(1), so no need to store size.
    """
    def get_size(self):
        return len(self._candles)


    """
    Return type: <Instrument> instance
    """
    def get_instrument(self):
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


    """
    Return type: datetime
    Return the time and date of the last candlestick.
    """
    def get_end_timestamp(self):
        return self._candles[self._end_index].timestamp


    """
    Return type: datetime.timedelta
    Get time difference between first and last candles.
    """
    def get_time_span(self):
        return self.get_end_timestamp() - self.get_start_timestamp(self)


    """
    Return type: datetime.timedelta
    Returns time difference between the last candlestick and now.
    """
    def get_lag(self):
        return datetime.utcnow() - get_end_timestamp()


    """
    """
    def _increment_start_index(self):
        if self._start_index < self.get_size() - 1:
            self._start_index += 1
        elif self._start_index == self.get_size() - 1:
            self._start_index = 0
        else:
            raise Exception
        if self._end_index < self.get_size() - 1:
            self._end_index += 1
        elif self._end_index == self.get_size() - 1:
            self._end_index = 0
        else:
            raise Exception


    """
    Return type: None on failure, 0 on success
    Basically re-initialize the chart.
    Use this for storing candles from a particular point in time.
    Use update() to get the latest candles.
    """
    def set(self, start_time):
        raise NotImplementedError


    """
    Return type: void
    Replace the candles with the most recent ones available.
    Algorithm: (TODO)
        Get the time difference from chart end to now.
        If the time difference is greater than the width of the chart,
            request <chart size> candles.
        else,
            request candles from end of chart to now.
    """
    def update(self):
        new_history = None
        if self.get_lag() > self.get_time_span():
            # replace all candles
            new_history = broker.get_instrument_history(
                instrument=self._instrument,
                granularity=self._granularity,
                count=self.get_size(), 
                end=datetime.utcnow()
            )
        else:
            new_history_ = broker.get_instrument_history(
                instrument=self._instrument,
                granularity=self._granularity,
                start=self.get_end_timestamp
            )
        if new_history == None:
            Log.write('chart.py update(): Failed to get new candles.')
            raise Exception
        else:
            # Got new candles. Stow them.
            new_candles = new_history['candles']
            # iterate forwards from last candle
            for i in range(0, len(self._candles)):
                # TODO assuming bid/ask candles
                # increment end index and overwrite the last candle
                self._increment_start_index() 
                self._candles[self._end_index].timestamp    = util_date.string_to_date(new_candle['time'])
                self._candles[self._end_index].volume       = float(new_candle['volume'])
                self._candles[self._end_index].complete     = bool(new_candle['complete'])
                self._candles[self._end_index].chart_format = new_candle['chartFormat']
                self._candles[self._end_index].open_bid     = float(new_candle['openBid'])
                self._candles[self._end_index].open_ask     = float(new_candle['openAsk'])
                self._candles[self._end_index].high_bid     = float(new_candle['highBid'])
                self._candles[self._end_index].high_ask     = float(new_candle['highBid'])
                self._candles[self._end_index].low_bid      = float(new_candle['lowBid'])
                self._candles[self._end_index].low_ask      = float(new_candle['lowAsk'])
                self._candles[self._end_index].close_bid    = float(new_candle['closeBid'])
                self._candles[self._end_index].close_ask    = float(new_candle['closeAsk'])


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


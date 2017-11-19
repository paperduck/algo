
import array

from broker import Broker
from instrument import Instrument

"""
A <Chart> is a group of sequential <Candle>s.
"""
class Chart:
    
    """
    A new <Chart> instance is empty.
    Fill it by calling update().
    """
    def __init__(self, instrument, size, granularity):
        # verify instance of <Instrument> by accessing a member.
        if instrument.get_id() == 0:
            pass            
        
        self._instrument = instrument   # <Instrument>
        self._start_index = 0           # int
        self._candles = []              # [<Candle>]
        self._granularity = granularity # string - see Oanda's documentation

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
    Return type: TODO
    """
    def get_instrument(self)
        return 'USD_JPY'


    """
    Return type: TODO
    """
    def get_granularity(self):
        return self._granularity


    """
    """
    def get_start_timestamp(self):
        return self._candles[self._start_index].timestamp


    """
    Return the time and date of the last candlestick.
    """
    def get_end_timestamp(self):
        return self._candles[self._end_index].timestamp


    """
    Return type: datetime.timedelta
    Get time difference between first and last candles.
    """
    def get_time_span(self):
        return self.get_end_timestamp - self.


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


    """
    Return type: void
    This wipes out all candles.
    set() or update() should be called after calling this.
    """
    def resize(self, new_size):
        raise NotImplementedError


    """
    Return type: void
    Use this for storing candles from a particular point in time.
    Use update() to get the latest candles.
    """
    def set(self, start_time)
        raise NotImplementedError


    """
    Return type: void
    Replace the candles with the most recent ones available.
    Algorithm:
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
            history = broker.get_instrument_history(
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
            Log.write('chart.py update(): New candles are None.')
            raise Exception
        else:
            # Got new candles. Stow them.
            new_candles = new_history['candles']
            # iterate forwards from last candle
            for i in range(0, len(self._candles)):
                # TODO assuming bid/ask candles
                self._candles[self._start_index].timestamp  = (float)new_candle['time']
                self._candles[self._start_index].volume     = (float)new_candle['volume']
                self._candles[self._start_index].complete   = (float)new_candle['complete']
                self._candles[self._start_index].open_bid   = (float)new_candle['openBid']
                self._candles[self._start_index].open_bid   = (float)new_candle['openBid']
                self._candles[self._start_index].open_bid   = (float)new_candle['openBid']
                self._candles[self._start_index].open_bid   = (float)new_candle['openBid']
                self._candles[self._start_index].open_bid   = (float)new_candle['openBid']
                self._candles[self._start_index].open_bid   = (float)new_candle['openBid']
                self._candles[self._start_index].open_bid   = (float)new_candle['openBid']
                self._candles[self._start_index].open_bid   = (float)new_candle['openBid']
        

    """
    Return type: <Candle>
    Parameter:  Type:
    key         int
    Description: Get the candle at a certain index.  Hide the offset of the
        internal start index.
    """
    def __getitem__(self, key):
        if key < 0 or key >= len(self._candles):
            raise Exception
        return self._candles[(key + self._start_index) % len(self._candles)]


    """
    There should be no reason to implement this.
    """
    def __setitem__(self, key, value):
        raise NotImplementedError


    """
    Return type: float
    Parameter:  Type:   Description
    start       int     Start index of slice. Defaults to chart start.
    end         int     End index of slice. Defaults to chart end.
    """
    def standard_deviation(self, start=0, end=len(self._candles)):
        raise NotImplementedError


    """
    Return type: probably float in a certain range
    Parameter:  Type:   Description:
    start       int     Index of slice start. Defaults to chart start.
    end         int     Index of slice end. Defaults to chart end.
    """
    def linearity(self, start=0, end=(len(self._candles) - 1)):
 55     # pearson coefficient
        raise NotImplementedError


    """
    """
    def slope(self, something):
 56     # "simple linear regression" or just two point slope
        raise NotImplementedError


    """
    not really sure
    """    
    def noise(self, start=0, end=(len(self._candles) - 1)):
        raise NotImplementedError
    

    """        
    # Anscombe's quartet
    """


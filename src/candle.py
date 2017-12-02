
"""
Class that represents a chart candlestick
"""
class Candle():

    def __init__(self,
        timestamp=None,     # datetime
        volume=None,        # int
        complete=None,      # bool

        open_bid=None,      # float
        open_ask=None,      # float
        open_mid=None,      # float
        high_bid=None,      # float
        high_ask=None,      # float
        high_mid=None,      # float
        low_bid=None,       # float
        low_ask=None,       # float
        low_mid=None,       # float
        close_bid=None      # float
        close_ask=None      # float
        close_mid=None      # float
    ):
        self.timestamp = timestamp     
        self.volume     = int(volume)   
        self.complete    = complete

        self.open_bid  = float(open_bid)
        self.open_ask  = float(open_ask)
        self.open_mid  = float(open_mid)
        self.high_bid  = float(high_bid)
        self.high_ask  = float(high_ask)
        self.high_mid  = float(high_mid)
        self.low_bid   = float(low_bid)
        self.low_ask   = float(low_ask)
        self.low_mid   = float(low_mid)
        self.close_bid = float(close_bid)
        self.close_ask = float(close_ask)
        self.close_mid = float(close_mid)


    def __del__(self):
        pass


    def __str__(self):
        return "{0} open:({1}) high:({2}) low:({3}) close:({4})"
            .format(
                self.timestmap, str(self.h), str(self.l), str(self.o), str(self.c)
            )




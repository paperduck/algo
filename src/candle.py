
"""
Class that represents a chart candlestick
"""
class Candle():

    """
    
    """
    def __init__(self,
        timestamp=None,     # datetime
        volume=None,        # int
        complete=None,      # bool
        chart_format=None,  # 'bidask' (default) or 'midpoint'

        open_bid=None,      # float
        open_ask=None,      # float
        open_mid=None,      # float
        high_bid=None,      # float
        high_ask=None,      # float
        high_mid=None,      # float
        low_bid=None,       # float
        low_ask=None,       # float
        low_mid=None,       # float
        close_bid=None,     # float
        close_ask=None,     # float
        close_mid=None      # float
    ):
        self.timestamp = timestamp     
        self.volume     = int(volume)   
        self.complete    = complete

        if open_bid != None:
            self.open_bid  = float(open_bid)
        if open_ask != None:
            self.open_ask  = float(open_ask)
        if open_mid != None:
            self.open_mid  = float(open_mid)
        if high_bid != None:
            self.high_bid  = float(high_bid)
        if high_ask != None:
            self.high_ask  = float(high_ask)
        if high_mid != None:
            self.high_mid  = float(high_mid)
        if low_bid != None:
            self.low_bid   = float(low_bid)
        if low_ask != None:
            self.low_ask   = float(low_ask)
        if low_mid != None:
            self.low_mid   = float(low_mid)
        if close_bid != None:
            self.close_bid = float(close_bid)
        if close_ask != None:
            self.close_ask = float(close_ask)
        if close_mid != None:
            self.close_mid = float(close_mid)


    def __del__(self):
        pass


    def __str__(self):
        return 'candle({0}) bid o:{1} h:{2} l:{3} c:{4}'.format(
            self.timestamp, str(self.open_bid), str(self.high_bid),
            str(self.low_bid), str(self.close_bid)
        )


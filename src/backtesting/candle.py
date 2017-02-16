
# numeric values of a candlestick
class candle():

    def __init__(self, date=None,time=None,high=None,low=None,op=None,close=None,volume=None):
        self.date       = date
        self.time       = time
        self.h          = float(high)
        self.l          = float(low)
        self.o          = float(op)
        self.c          = float(close)
        self.volume     = int(volume)
        pass

    def __del__():
        pass

    def __str__():
        return "open:({0}) high:({1}) low:({2}) close:({3})".format(\
            str(self.h), str(self.l), str(self.o), str(self.c) )

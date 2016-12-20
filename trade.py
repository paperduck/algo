#!/usr/bin/python3
# Python 3.4
# trade.py
# Description: Class that represents an Oanda trade.

class trade():
    
    def __init__(self, trade_id, instrument):
        self.trade_id = trade_id
        self.instrument = instrument
    

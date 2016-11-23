#!/usr/bin/python3
# Python 3.4
# trade.py
# Description: Class that represents an Oanda trade.

class trade():
    
    def __init__(self, in_id, in_instrument):
        self.trade_id = in_id
        self.instrument = in_instrument
    

# -*- coding: utf-8 -*-

"""
Description:
    Class to store order info.
    It is generic for all brokers, so if more brokers are added in the
    future, this may need to be tweaked.
"""

class Order():

    def __init__(self, instrument, units, side, order_type, expiry=None, price=None,\
    lower_bound=None, upper_bound=None, stop_loss=None, take_profit=None,\
    trailing_stop=None, transaction_id=None, confidence=0, reason=''):
        self.instrument     = instrument
        self.units          = units
        self.side           = side
        self.order_type     = order_type
        self.expiry         = expiry
        self.price          = price
        self.lower_bound    = lower_bound
        self.upper_bound    = upper_bound
        self.stop_loss      = str(stop_loss)
        self.take_profit    = str(take_profit)
        self.trailing_stop  = trailing_stop
        self.transaction_id = transaction_id




# -*- coding: utf-8 -*-

####################
from log import Log
####################

class Order():
    """
    Description:
        Class container for order info.
        It is generic for all brokers, so if more brokers are added in the
        future, this may need to be tweaked.
    """

    def __init__(
        self,
        instrument=None,        # <Insrument>
        order_type=None,        # string - limit/stop/marketIfTouched/market
        price=None,             # numeric, prince per unit for limit/stop/marketIfTouched
        lower_bound=None,       #
        stop_loss=None,         # JSON
        take_profit=None,       # JSON
        trailing_stop=None,     # JSON
        units=None,             # numeric; use negative for short
        upper_bound=None,
        reason=''               # optional string - for logging
    ):
        self.instrument     = instrument
        self.lower_bound    = lower_bound
        self.order_type     = order_type
        self.price          = price
        self.stop_loss      = stop_loss
        self.take_profit    = take_profit
        self.trailing_stop  = trailing_stop
        self.units          = units
        self.upper_bound    = upper_bound
        self.reason         = reason


    def __str__(self):
        return '\n\
            instrument: {}\n\
            lower_bound: {}\n\
            order_type: {}\n\
            price: {}\n\
            stop_loss: {}\n\
            take_profit: {}\n\
            trailing_stop: {}\n\
            units: {}\n\
            upper_bound: {}\n\
            reason: {}\n'.format(
                self.instrument.get_name(),
                self.lower_bound,
                self.order_type,
                self.price,
                self.stop_loss,
                self.take_profit,
                self.trailing_stop,
                self.units,
                self.upper_bound,
                self.reason
            )


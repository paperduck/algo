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
        go_long=None,           # boolean
        order_type=None,        # string - limit/stop/marketIfTouched/market
        expiry=None,            # date/time as string (util_date.py)
        price=None,             # numeric, prince per unit for limit/stop/marketIfTouched
        lower_bound=None,       #
        stop_loss=None,         # 
        take_profit=None,
        trailing_stop=None,
        #transaction_id=None,
        units=None,             # numeric
        upper_bound=None,
        reason=''               # optional string - for logging
    ):
        self.expiry         = expiry
        self.instrument     = instrument
        self.lower_bound    = lower_bound
        self.order_type     = order_type
        self.price          = price
        self.go_long        = go_long
        self.stop_loss      = str(stop_loss)
        self.take_profit    = str(take_profit)
        self.trailing_stop  = trailing_stop
        #self.transaction_id = transaction_id
        self.units          = units
        self.upper_bound    = upper_bound
        self.reason         = reason


    def __str__(self):
        return '\n\
            expiry: {}\n\
            instrument: {}\n\
            lower_bound: {}\n\
            order_type: {}\n\
            price: {}\n\
            long: {}\n\
            stop_loss: {}\n\
            take_profit: {}\n\
            trailing_stop: {}\n\
            units: {}\n\
            upper_bound: {}\n\
            reason: {}\n'.format(
                self.expiry,
                self.instrument.get_name(),
                self.lower_bound,
                self.order_type,
                self.price,
                self.go_long,
                self.stop_loss,
                self.take_profit,
                self.trailing_stop,
                self.units,
                self.upper_bound,
                self.reason
            )


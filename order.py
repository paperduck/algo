#!/usr/bin/python3

# Class to store order info for Oanda fxTrade REST API.
# The variables align with the fxTrade REST API for placing orders.

class order():

    def __init__(self, in_fav, in_ins, in_units, in_side, in_type, in_expiry, in_price,\
    in_lower_bound, in_upper_bound, in_stop_loss, in_take_profit, in_trailing_stop):
        self.fav = in_fav
        self.instrument = in_ins
        self.units = in_units
        self.side = in_side
        self.order_type = in_type
        self.expiry = in_expiry
        self.price = in_price
        self.lowerBound = in_lower_bound
        self.upperBound = in_upper_bound
        self.stopLoss = str(in_stop_loss)
        self.takeProfit = str(in_take_profit)
        self.trailingStop = in_trailing_stop





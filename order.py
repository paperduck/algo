#!/usr/bin/python3

# Class to store order info for Oanda fxTrade REST API.
# The variables align with the fxTrade REST API for placing orders.
# There are some extra fields as well.

class order():

    def __init__(self, in_instrument,in_units,in_side, in_type, in_expiry=None, in_price=None,\
    in_lower_bound = None, in_upper_bound = None, in_stop_loss = None, in_take_profit = None\
    ,in_trailing_stop=None, in_transaction_id=None, in_confidence=0, in_reason=''):
        self.instrument     = in_instrument
        self.units          = in_units
        self.side           = in_side
        self.order_type     = in_type
        self.expiry         = in_expiry
        self.price          = in_price
        self.lower_bound    = in_lower_bound
        self.upper_bound    = in_upper_bound
        self.stop_loss      = str(in_stop_loss)
        self.take_profit    = str(in_take_profit)
        self.trailing_stop  = in_trailing_stop
        self.transaction_id = in_transaction_id
        # extra fields
        self.confidence = in_confidence
        self.reason = ''    # reason why this trade should be entered        




#!/usr/bin/python3

"""
File:               trade.py
Python version:     3.4
Description:        Containers for trades.
"""

class trade():
    """
    Represents one trade, either past or present.
    Future trades are "opportunities" or "orders".
    """
    
    def __init__(self, transaction_id, instrument_id, strategy_name=None):
        self.transaction_id = transaction_id
        self.instrument_id = instrument_id
        self.strategy_name = strategy_name
   
    def __str__(self):
        msg = 'Transaction ID: {}\n\
               Instrument ID: {}\n\
               Strategy Name: {}'\
               .format(
               self.transaction_id,
               self.instrument_id,
               self.strategy_name
               )


class trades():
    """
    List of `trade` objects.
    """
    
    def __init__(self):
        self.trade_list = []


    def append(self, trade):
        self.trade_list.append(trade)


    def remove(self, transaction_id):
        """
        Remove the trade with the given transaction ID.
        
        Returns: Removed trade object on success; None on failure.
        """
        for i in range(0, len(self.trade_list)-1):
            if self.trade_list[i].transaction_id == transaction_id:
                return self.trade_list.pop[i]
        return None
    

    def fill_in_trade_extra_info(self):
        """
        Fill in info not provided by the broker, e.g.
        the name of the strategy that opened the trade.
 
        It's possible that a trade will be opened then the system is
        unexpectedly terminated before info about the trade can be saved to
        the database. Thus a trade passed to this
        function may not have a corresponding trade in the database.

        Returns: Bool (0=success 1=failure)
        """
        # TODO
        for t in self.trade_list:
            pass




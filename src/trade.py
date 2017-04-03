"""
File:               trade.py
Python version:     3.4
Description:        Containers for trades.
"""

####################
from collections.abc import Sequence
####################


class Trade():
    """
    Represents one trade, either past or present.
    Future trades are "opportunities" or "orders".
    """
    
    def __init__(self,
        instrument=None,        # TODO, using strings for now
        side=None,              # 'buy' / 'sell'
        stop_loss=None,         # numeric
        strategy=None,          # <Strategy>
        take_profit=None,       # numeric
        trade_id=None     # string
    ):
        self.instrument     = instrument
        self.side           = side
        self.stop_loss      = stop_loss
        self.strategy       = strategy
        self.take_profit    = take_profit
        self.trade_id = trade_id
   

    def __str__(self):

        strategy_name = "(unknown)"
        if self.strategy != None:
            strategy_name = self.strategy.name
        msg = 'Transaction ID: {}\n\
            Instrument: {}\n\
            Strategy: {}'\
            .format(
                self.trade_id,
                self.instrument,
                strategy_name
            )
        return msg


class Trades(Sequence):
    """
    List of `trade` objects.
    TODO:  This could be a heap, with the trade's ID as the key.
    """
    
    def __init__(self):
        self._trade_list = []
        self.current_index = 0

    def append(self, trade):
        self._trade_list.append(trade)


    def pop(self, trade_id):
        """
        Remove the trade with the given transaction ID.
        
        Returns: Removed trade object on success; None on failure.
        """
        index = 0
        for t in self._trade_list:
            if t.trade_id == trade_id:
                return self._trade_list.pop(index)
            index = index + 1
        return None


    def length(self):
        return len(self._trade_list)    


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
        for t in self._trade_list:
            pass


    def __iter__(self):
        """
        Make this class iterable
        https://docs.python.org/3/library/stdtypes.html#typeiter
        """
        return self


    def __next__(self):
        """
        Make this class iterable
        """
        if self.current_index >= len(self._trade_list):
            self.current_index = 0
            raise StopIteration
        else:
            self.current_index = self.current_index + 1
            return self._trade_list[self.current_index - 1]


    def __getitem__(self, key):
        """
        Expose index operator.
        """
        return self._trade_list[key]
    

    def __len__(self):
        """
        Expose len() function.
        """
        return len(self._trade_list)


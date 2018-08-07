"""
Python ver.   3.4
File:         strategy.py
Description:
    Base class for strategies defined here.
    This should NOT be instantiated directly.
    Derive it and make your own strategy.
"""

#*************************
import sys
#*************************
from config import Config
from db import DB
from log import Log
from trade import *
#*************************

class Strategy():
    """
    Class methods are used because the daemon never needs more than one
    instance of each strategy.
    """

    # 
    open_trade_ids = []


    def __str__(self):
        return self.get_name()


    def get_number_positions(self):
        return len( self.open_trade_ids )


    def get_name(self):
        """
        Needs to be overloaded.
        This is a method only instead of a string member in order to enforce
        implementation by derived classes. 
        Returns: Name of strategy as a unique string.
        """
        raise NotImplementedError()


    def trade_opened(self,  trade_id):
        """ Called by the daemon to notify the strategy that the order it suggested has been placed.
        Return type: void
        Parameters:
            trade_id        string
        """
        self.open_trade_ids.append(trade_id)
        Log.write('"strategy.py" trade_opened(): strat {} opened trade ({})'
            .format(self.get_name(), trade_id)) 
        # Write to db - mainly for backup in event of power failure
        DB.execute('INSERT INTO open_trades_live (trade_id, strategy, \
            broker) values ("{}", "{}", "{}")'
            .format(trade_id, self.get_name(), Config.broker_name))


    def adopt(self, trade_id):
        """
        When the daemon is initializing, particularly after being unexpectedly
        terminated, this can be used to tell the strategy
        module about a trade that it had previously opened.
        """
        self.open_trade_ids.append(trade_id)


    def cleanup(self):
        """ release memory """
        del self.open_trade_ids[:]


    def refresh(self):
        """The daemon should call this repeatedly."""
        self._babysit()
        return self._scan()


    def _babysit(self):
        """
        Return type: void
        Babysit open trades.
        Override this in your strategy module.
        """
        raise NotImplementedError()
 

    def _scan(self):
        """
        Determines whether there is an opportunity or not.
        Override this in your strategy module.
        Return type:
            <Opportunity> instance if there is an opportunity.
            None if no opportunity.
        """
        raise NotImplementedError()



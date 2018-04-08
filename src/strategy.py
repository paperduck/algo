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
    _open_trade_ids = []


    @classmethod
    def __str__(cls):
        return cls.get_name()


    @classmethod
    def get_number_positions(cls):
        return _open_trade_ids.size()


    @classmethod
    def get_name(cls):
        """
        Needs to be overloaded.
        This is a method only instead of a string member in order to enforce
        implementation by derived classes. 
        Returns: Name of strategy as a unique string.
        """
        raise NotImplementedError()


    """
    Return type: void
    Called by the daemon to notify the strategy that the order it suggested
        has been placed.
    """
    @classmethod
    def trade_opened(
        cls,
        trade_id    # string
    ):
        cls._open_trade_ids.append(trade_id)
        Log.write('"strategy.py" trade_opened(): strat {} opened trade ({})'
            .format(cls.get_name(), trade_id)) 
        # Write to db
        DB.execute('INSERT INTO open_trades_live (trade_id, strategy, \
            broker) values ("{}", "{}", "{}")'
            .format(trade_id, cls.get_name(), Config.broker_name))


    """
    Return type: True on success (TODO: for consitency use 0)
    Description:
        This must be called to notify a strategy that one of its trades
        has closed.
        Probably only called by daemon.py since that is currently the
        only module that has access to individual strategy modules.
    Input:      trade id from broker (string)
    """
    @classmethod
    def trade_closed(
        cls,
        trade_id   # string - trade id from broker
    ):
        Log.write('"strategy.py" trade_closed(): Attempting to pop trade ',
            'ID {}'.format(trade_id))
        # Remove the trade from the list.
        # TODO: Put a lock on cls._open_trade_ids to make it thread safe while
        # deleting from it.
        num_trades = len(cls._open_trade_ids)
        if num_trades > 0:
            closed_trade_id = None
            for i in range(0, num_trades):
                if cls._open_trade_ids[i] == trade_id:
                    closed_trade_id = cls._open_trade_ids.pop(i)
                    break
            # Make sure the trade was actually popped.
            if closed_trade_id == None:
                Log.write('"strategy.py" trade_closed(): Strategy ',
                    '"{}" failed to pop trade {} from _open_trades.'
                    .format(cls.get_name(), closed_trade_id))
                raise Exception
            else:
                Log.write('"strategy.py" trade_closed(): Trade of strategy ',
                 '"{}" has closed.'.format(cls.get_name()))
                return True
            # Update list of live trades in database
            DB.execute('DELETE FROM open_trades_live WHERE trade_id LIKE {}'
                .format(trade_id))
        else:
            # Not tracking any trades! Oh no.
            err_msg = '"strategy.py" trade_closed(): Trade closed but list of open trades is empty!'
            Log.write(err_msg)
            DB.bug(err_msg)
            raise Exception


    """
    Return value: void
    Description:    This must be called when a trade is reduced.
    """
    @classmethod
    def trade_reduced(cls,
        trade,          # <Trade>
        instrument_id   # database ID (instruments.id)
    ):
        # TODO: write to db
        Log.write('"strategy.py" trade_reduced(): Trade {} was reduced.'
            .format(cls.get_name()))
        pass


    # TODO maybe call this function "adopt" to make it more generic
    @classmethod
    def recover_trade(cls, trade_id):
        """
        When the daemon is initializing, particularly after being unexpectedly
        terminated, this can be used to tell the strategy
        module about a trade that it had previously opened.
        """
        cls._open_trade_ids.append(trade_id)


    @classmethod
    def drop_all(cls):
        del cls._open_trade_ids[:]


    """
    Override this in your strategy module.
    The daemon calls this repeatedly.
    """
    @classmethod
    def refresh(cls):
        cls._babysit()
        return cls._scan()


    """
    Return type: void
    Babysit open trades.
    Override this in your strategy module.
    """
    @classmethod
    def _babysit(cls):
        raise NotImplementedError()
 

    """
    Return type:
        <Opportunity> instance if there is an opportunity.
        None if no opportunity.
    Override this in your strategy module.
    Determines whether there is an opportunity or not.
    """
    @classmethod
    def _scan(cls):
        raise NotImplementedError()



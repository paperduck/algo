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
from log import Log
from trade import *
#*************************

class Strategy():
    """
    Class methods are used because the daemon never needs more than one
    instance of each strategy.
    """

    #List of trade (transaction) IDs. TODO: Might use [<Trade>] in the future.
    _open_trade_ids = []


    @classmethod
    def get_name(cls):
        """
        Needs to be overloaded.
        This is a method only instead of a string member in order to enforce
        implementation by derived classes. 
        Returns: Name of strategy as a unique string.
        """
        raise NotImplementedError()


    @classmethod
    def __str__(cls):
        return cls.get_name()


    @classmethod
    def trade_opened(cls, trade_id, instrument_id):
        """
        Description:
            This must be called to notify the strategy when an order that it
            suggested was placed.
            Probably only called by daemon.py since that is currently the
            only module that has access to individual strategy modules.
        Input:      trade id from broker
        Returns:
        """
        cls._open_trade_ids.append(trade_id)
        Log.write('"strategy.py" trade_opened(): Hooray, strategy {} ',
            'opened a trade with ID "{}"'.format(cls.get_name(), trade_id)) 
        Log.write('"strategy.py" trade_opened(): cls._open_trade_ids contains:')
        Log.write(cls._open_trade_ids)
        # Write to db
        DB.execute('INSERT INTO open_trades_live (trade_id, strategy, \
            broker, instrument_id) values ("{}", "{}", "{}", {})'
            .format(trade_id, cls.get_name(), Config.broker_name, instrument_id))


    @classmethod
    def trade_closed(cls, trade_id, instrument_id):
        """
        Description:
            This must be called to notify a strategy that one of its trades
            has closed.
            Probably only called by daemon.py since that is currently the
            only module that has access to individual strategy modules.
        Input:      trade id from broker (string)
        Returns: 
        """
        Log.write('"strategy.py" trade_closed(): Attempting to pop trade ',
            'ID {}'.format(trade_id))
        # Remove the trade from the list.
        # TODO: Put a lock on cls._open_trade_ids to make it thread safe while
        # deleting from it.
        num_trades = len(cls._open_trade_ids)
        if num_trades > 0:
            closed_trade = None
            for i in range(0, num_trades):
                if cls._open_trade_ids[i] == trade_id:
                    closed_trade = cls._open_trade_ids.pop(i)
                    break
            # Make sure the popping went well.
            if closed_trade == None:
                Log.write('"strategy.py" trade_closed(): Strategy ',
                    '"{}" failed to pop trade {} from _open_trade_ids.'
                    .format(cls.get_name(), trade_id))
                Log.write('"strategy.py" trade_closed(): cls._open_trade_ids ',
                    'contains: {}'.format(cls._open_trade_ids))
                sys.exit()
            else:
                Log.write('"strategy.py" trade_closed(): Trade of strategy ',
                 '"{}" has closed.'.format(cls.get_name()))
                # Send trade info to strategy
                cls._trade_closed(trade_id)
                return True
            # Write to db
            DB.execute('DELETE FROM open_trade_ids_live WHERE trade_id LIKE {}'
                .format(trade_id))
        else:
            # Not tracking any trades! Oh no.
            err_msg = '"strategy.py" trade_closed(): Trade closed but list of open trades is empty!'
            Log.write(err_msg)
            DB.bug(err_msg)
            Daemon.shutdown()


    @classmethod
    def trade_reduced(cls, trade_id, instrument_id):
        """
        Description:    This must be called when a trade is reduced.
        Parameters:
                        trade_id        ID of trade, assigned by broker
                        instrument_id   database: instruments.id
        Returns:        (nothing)
        """
        # TODO: write to db
        Log.write('"strategy.py" trade_reduced(): Trade {} was reduced.'
            .format(cls.get_name()))
        pass


    # TODO maybe call this function "adopt" to make it more generic
    @classmethod
    def recover_trade(cls, trade):
        """
        When the daemon is initializing, particularly after being unexpectedly
        terminated, this can be used to tell the strategy
        module about a trade that it had previously opened.
        """
        cls._open_trade_ids.append(trade)


    @classmethod
    def drop_all(cls):
        """
        """
        del cls._open_trade_ids[:]


    @classmethod
    def refresh(cls):
        """
        The daemon should call this over and over.
        """
        cls._babysit()
        return cls._scan()


    @classmethod
    def _babysit(cls):
        """
        This needs to be implemented by a strategy module.
        Babysit open trades.
        """
        raise NotImplementedError()
 

    @classmethod
    def _scan(cls):
        """
        This needs to be implemented by a strategy module.
        Look at current price and past prices and determine whether there is
        an opportunity or not.
        Returns:
            If the daemon should enter a trade, an instance of `order',
            otherwise None.
        """
        raise NotImplementedError()



"""
Python ver.   3.4
File:         strategy.py
Description:
    Base class for strategies defined here.
    Backup babysitter class is defined here.
"""

#*************************
import sys
#*************************
from log import Log
from trade import *
#*************************

class Strategy():
    """
    Class methods are used because the daemon never needs more than one
    instance of each strategy.
    """

    #List of trade (transaction) IDs. TODO: Might use [<Trade>] in the future.
    _open_trades = []


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
    def trade_opened(cls, trade_id):
        """
        Description:
            This must be called to notify the strategy when an order that it
            suggested was placed.
            This is separate from recover_trade() just in case I want to do
            something different in either function later.
        Input: 
            trade id from broker
        Returns:
        """
        cls._open_trades.append(trade_id)
        Log.write('"strategy.py" trade_opened(): Hooray, strategy {} ',
            'opened a trade with ID "{}"'.format(cls.get_name(), trade_id)) 
        Log.write('"strategy.py" trade_opened(): cls._open_trades contains:')
        Log.write(cls._open_trades)
        # TODO: write to db


    @classmethod
    def trade_closed(cls, trade_id):
        """
        Description:
            This must be called to notify a strategy that one of its trades
            has closed.
        Input:
            trade id from broker (string)
        Returns: 
        """
        Log.write('"strategy.py" trade_closed(): Attempting to pop trade ',
            'ID {}'.format(trade_id))
        # Remove the trade from the list.
        # TODO: Put a lock on cls._open_trades to make it thread safe while
        # deleting from it.
        num_trades = len(cls._open_trades)
        if num_trades > 0:
            closed_trade = None
            for i in range(0, num_trades):
                if cls._open_trades[i] == trade_id:
                    closed_trade = cls._open_trades.pop(i)
                    Log.write('match')
                else:
                    Log.write(cls._open_trades[i], ' does not match ', trade_id)
            # Make sure the popping went well.
            if closed_trade == None:
                Log.write('"strategy.py" trade_closed(): Strategy ',
                    '"{}" failed to pop trade from _open_trades.'
                    .format(cls.get_name()))
                #return False
                Log.write('"strategy.py" trade_closed(): Looked for trade ID ',
                    '{}'.format(trade_id))
                Log.write('"strategy.py" trade_closed(): cls._open_trades contains:')
                Log.write(cls._open_trades)
                print('Aborting')
                sys.exit()
            else:
                Log.write('"strategy.py" trade_closed(): Trade of strategy "{}" has closed.'
                    .format(cls.get_name()))
                return True
            # TODO: write to db
        else:
            # Not tracking any trades! Oh no.
            Log.write('"strategy.py" trade_closed(): Trade closed but list of open trades is empty!')
            Log.write('"strategy.py" trade_closed(): Aborting.')
            sys.abort()


    @classmethod
    def trade_reduced(cls, trade_id):
        """
        Description:    This must be called when a trade is reduced.
        """
        # TODO: write to db
        Log.write('"strategy.py" trade_reduced(): Trade {} was reduced.'
            .format(cls.get_name()))
        pass


    @classmethod
    def recover_trade(cls, trade):
        """
        When the daemon is initializing, particularly after being unexpectedly
        terminated, this can be used to tell the strategy
        module about a trade that it had previously opened.
        """
        cls._open_trades.append(trade.trade_id)


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


'''
class BackupBabysitter(Strategy):
    """
    Class used for babysitting orphan trades.
    An orphan trade is a trade that is not assigned to a strategy.
    Orphan trades can result from this sequence of events:
        - A strategy places an order that opens a trade
        - The daemon is terminated improperly (not a clean shutdown)
        - Information about the trade is not written to the database
        - The daemon starts again and sees that a trade is open, but there
            is no information about that trade in the database.
    Class methods are used because there is no need for more than one
        backup babysitter.
    """
    

    @classmethod
    def babysit(cls):
        """
        Same as the _babysit() function in the base Strategy class.
        """
        # TODO
        for t in cls._open_trades:
            Log.write('"strategy.py" babysit(): Working hard!')


    @classmethod
    def adopt(cls, trade):
        """
        This method is used to assign a trade to BackupBabysitter.
        This is the same as Strategy.recover_trade().
        However, the name is different because in this class, unlike in the
        Strategy class, there is no need to
        differentiate between trade_opened() and recover_trade().
        """
        cls._open_trades.append(trade)
'''



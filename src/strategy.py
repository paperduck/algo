"""
Python ver.   3.4
File:         strategy.py
Description:
    Base class for strategies defined here.
    Backup babysitter class is defined here.
"""

#*************************
#*************************
from log import Log
from trade import *
#*************************

class Strategy():
    """
    Class methods are used because the daemon never needs more than one
    instance of each strategy.
    """

    @classmethod
    def __init__(cls):
        cls.name = None  # strategy name
        """
        Initialize a list of trades opened by this strategy. 
        If the derived strategy class has its own __init__ function, then
        this needs to be initialized there.
        """
        #cls.open_trades = []   # list of <trade>

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
        cls.open_trades.append(trade)
        Log.write('"strategy.py" trade_opened(): Hooray, {} opened a trade!'
            .format(cls.name))
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
        #raise NotImplementedError()
        # Remove the trade from the list.
        closed_trade = None
        for i in range(1, len(cls.open_trades)):
            if cls.open_trades[i].transaction_id == transaction_id:
                closed_trade = cls.open_trades.pop[i-1]
        # Make sure the popping went well.
        if closed_trade == None:
            Log.write('"strategy.py" trade_closed(): {} failed to pop trade\
                from open_trades.'.format(cls.name))
            return False
        else:
            Log.write('"strategy.py" trade_closed(): Hooray, {} closed a trade!'
                .format(cls.name))
            return True
        # TODO: write to db


    @classmethod
    def trade_reduced(cls, trade_id):
        """
        Description:    This must be called when a trade is reduced.
        """
        # TODO: write to db
        Log.write('"strategy.py" trade_reduced(): Trade {} was reduced.'
            .format(cls.name))
        pass


    @classmethod
    def recover_trade(cls, trade):
        """
        When the daemon is initializing, particularly after being unexpectedly
        terminated, this can be used to tell the strategy
        module about a trade that it had previously opened.
        """
        cls.open_trades.append(transaction_id)


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


class BackupBabysitter():
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
    def __init__(cls):
        cls.open_trades = []


    @classmethod
    def babysit(cls):
        """
        Same as the babysit() function in the base Strategy class.
        """
        # TODO
        for t in cls.open_trades:
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
        cls.open_trades.append(trade)


# -*- coding: utf-8 -*-

"""
File            broker_api.py
Python ver.     3.4
Description     Python module that provides a generic layer between
                the daemon and the broker-specific code.
"""

#****************************
import configparser
import sys
#****************************
from log import *
from oanda import *
#****************************

class Broker():

    # read in which broker/dealer to use from the config file
    cfg = configparser.ConfigParser()
    cfg.read('config_nonsecure.cfg')
    config_path = cfg['config_secure']['path']
    cfg.read(config_path)
    broker_name = cfg['trading']['broker']
    if broker_name == None:
        log.write('"broker.py" __init__(): Failed to get broker from config file.')
        sys.exit()
    if broker_name == 'oanda':
        broker = Oanda
    else:
        log.write('"broker.py" __init__(): Unknown broker name')
        sys.exit()

    @classmethod
    def is_practice(cls):
        return cls.broker.practice

    # Get authorization key.
    @classmethod
    def get_auth_key(cls):
        return cls.broker.get_auth_key()


    # Get list of accounts
    # Returns: dict or None
    @classmethod
    def get_accounts(cls):
        return cls.broker.get_accounts()
   
 
    # Get list of open positions
    # Returns: dict or None 
    @classmethod
    def get_positions(cls, account_id):
        return cls.broker.get_positions(account_id)


    # Get number of positions for a given account ID
    # Returns: Integer
    @classmethod
    def get_num_of_positions(cls, account_id):
        return cls.broker.get_num_of_positions(account_id)


    # Get account balance for a given account ID
    # Returns: Decimal number
    @classmethod
    def get_balance(cls, account_id):
        return cls.broker.get_balance(account_id)


    @classmethod
    def get_prices(cls, instruments, since=None):
        """
        Fetch live prices for specified symbol(s)/instrument(s).
        Returns: dict or None
        TODO: make this more robust. Maybe pass in a list, then have each broker-specific library
            do validation.
        """
        return cls.broker.get_prices(instruments, since)


    @classmethod
    def get_ask(cls, instrument, since=None):
        """
        Get one ask price
        Returns: Decimal or None
        """
        return cls.broker.get_ask(instrument, since)


    @classmethod
    def get_bid(cls, instrument, since=None):
        """
        # Get one bid price
        # Returns: Decimal or None
        """
        return cls.broker.get_bid(instrument, since)


    @classmethod
    def get_spreads(cls, symbols, since=None):
        """
        Returns: dict of (<symbol>, <spread>) tuples.
        """
        return cls.broker.get_spreads(symbols, since)


    @classmethod
    def get_spread(cls, symbol, since=None):
        """
        Get one spread value

        Returns: Decimal/Float
        """
        return cls.broker.get_spread(symbol, since)


    @classmethod
    def place_order(cls, in_order):
        """
        Place an order.
        
        Return: ???dict??? or None
        """
        result = cls.broker.place_order(in_order)
        # TODO: If a trade is opened, write trade info to db
        # (table: live_open_trades)
        # if result then: write to db
        return result

    @classmethod
    def is_market_open(cls):
        """
        Is the market open?

        Returns: Boolean
        """
        return cls.broker.is_market_open()


    @classmethod
    def get_transaction_history(cls, maxId=None, minId=None, count=None, instrument=None, ids=None):
        """
        # Get transaction history
        # Returns: dict or None
        """
        return cls.broker.get_transaction_history(maxId=maxId, minId=minId,
            count=count, instrument=instrument, ids=ids)


    @classmethod
    def is_trade_closed(cls, transaction_id):
        """
        See if a trade is closed.
        Returns: Boolean or None
        """
        return cls.broker.is_trade_closed(transaction_id)


    @classmethod
    def get_trades(cls):
        """
        Get info about all open trades from the broker.
        To get more info about the trades, use
        trade.fill_in_trade_extra_info().

        Returns: dict or None
        """
        # First, get the information that the broker provides.
        # These `trade` instances will be missing the strategy names.
        log.write('"broker.py" get_trades(): entering')
        return cls.broker.get_trades()


    # Get info about a particular trade
    # Returns: dict or None
    @classmethod
    def get_trade(cls, trade_id):
        return cls.broker.get_trade(trade_id)


    # Get order info
    # Returns: dict or None
    @classmethod
    def get_order_info(cls, order_id):
        return cls.broker.get_order_info(order_id)

 
    @classmethod
    def modify_order(cls, in_order_id, in_units=0, in_price=0, in_expiry=0,
        in_lower_bound=0, in_upper_bound=0, in_stop_loss=0,
        in_take_profit=0, in_trailing_stop=0):
        """
        # Modify an existing order
        # Returns: dict or None
        """
        return cls.broker.modify_orders(locals())


    @classmethod
    def modify_trade(cls, in_trade_id, in_stop_loss=0, in_take_profit=0, in_trailing_stop=0):
        """
        # Modify an existing trade
        # Returns: dict or None
        """
        return cls.broker.modify_trade(locals()) 



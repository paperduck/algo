#!/usr/bin/python3

# File          
# Python ver.   3.4
# Description   Backtesting using historical data.
#               Organized to match Oanda REST API.
#               Intended to be used by a strategy module that will use the Oanda REST API.

#--------------------------
import configparser
import gzip
import json
import sys
import time                 # for sleep()
import urllib.request
import urllib.error
import zlib
#--------------------------
from log import log
import order
#--------------------------

class oanda():
    cfg = configparser.ConfigParser()
    cfg.read('/home/user/raid/documents/algo.cfg')
    practice = True
    pip_factors = {\
        'AUD_CAD':10000,\
        'AUD_CHF':10000,\
        'AUD_HKD':10000,\
        'AUD_JPY':100,\
        'AUD_USD':10000,\
        'EUR_USD':10000,\
        'GBP_JPY':100,
        'GBP_USD':10000,\
        'NZD_USD':10000,\
        'USD_CAD':10000,\
        'USD_CHF':10000,\
        'USD_JPY':100,
        }
    account_id_primary = 0

    open_trades = []
    closed_trades = []

    # Dictionary of "iterators"; one for each instrument (one per db table).    
    # All are synced to same time; get_next_candle() increments all of them.
    # Add instruments lazily; although there are limited forex pairs, in the
    #   case of stocks, it might be overkill to open all of them (potentially thousands).
    # Example:
    #   { 'USD_JPY':{ 'date':'2016-12-01', 'open':123.456 } }
    candles = {}

    #
    @classmethod
    def is_practice(cls):
        return cls.practice

    # Get authorization key.
    # Oanda was returning a '400 Bad Request' error 4 out of 5 times
    #   until I removed the trailing '\n' from the string
    #   returned by f.readline().
    @classmethod
    def get_auth_key(cls):
        return 1

    # Which REST API to use?
    @classmethod
    def get_rest_url(cls):
        return None
 
    # Decode bytes to string using UTF8.
    # Parameter `b' is assumed to have type of `bytes'.
    @classmethod
    def btos(cls, b):
        return b.decode('utf_8')
    #
    @classmethod
    def stob(cls, s):
        return s.encode('utf_8')

    # Helpful function for accessing Oanda's REST API
    # Returns JSON as a string, or None.
    # Prints error info to stdout.
    @classmethod
    def fetch(cls, in_url, in_headers=None, in_data=None, origin_req_host=None, unverifiable=False, method=None):
        return None

    # Get list of accounts
    # Returns: dict or None
    @classmethod
    def get_accounts(cls):
        return None

    # Get ID of account to trade with.
    # Returns: String
    @classmethod
    def get_account_id_primary(cls):
        return None

    # Get account info for a given account ID
    # Returns: dict or None 
    @classmethod
    def get_account(cls, account_id):
        return None

    # Get list of open positions
    # Returns: dict or None 
    @classmethod
    def get_positions(cls, account_id):
        return None

    # Get number of positions for a give account ID
    # Returns: Number
    @classmethod
    def get_num_of_positions(cls, account_id):
        return None

    # Get account balance for a given account ID
    # Returns: Decimal number
    @classmethod
    def get_balance(cls, account_id):
        return None

    # Fetch live prices for specified instruments that are available on the OANDA platform.
    # Returns: dict or None
    # `instruments' argument must be URL encoded comma-separated, e.g. USD_JPY%2CEUR_USD
    @classmethod
    def get_prices(cls, instruments, since=None):
        # lazy append requested instruments
        for i in instruments:
            cls.append_instrument(i)  # this modifies cls.candles
        return cls.candles

    # Get one ask price
    # Returns: Decimal or None
    @classmethod
    def get_ask(cls, instrument, since=None):
        #log.write('"oanda.py" get_ask(): Entering.')
        prices = cls.get_prices(instrument, since)
        if prices != None:
            for p in prices['prices']:
                if p['instrument'] == instrument:
                    return float(p['ask'])
        else:
            log.write('"oanda.py" get_ask(): Failed to get prices.')
            sys.exit()

    # Get one bid price
    # Returns: Decimal or None
    @classmethod
    def get_bid(cls, instrument, since=None):
        #log.write('"oanda.py" get_bid(): Entering. Getting bid of ', instrument, '.')
        prices = cls.get_prices(instrument, since)
        if prices != None:
            for p in prices['prices']:
                if p['instrument'] == instrument:
                    return float(p['bid'])
        else:
            log.write('"oanda.py" get_bid(): Failed to get prices.')
            sys.exit()

    # Given an instrument (e.g. 'USD_JPY') and price, convert price to pips
    # Returns: decimal or None
    @classmethod
    def to_pips(cls, instrument, value):
        #log.write('"oanda.py" to_pips(): Entering.')
        if instrument in cls.pip_factors:
            return cls.pip_factors[instrument] * value
        else:
            sys.exit()

    # Get spread, in pips, for given currency pairs (e.g. 'USD_JPY%2CEUR_USD')
    # Returns: dict of (<instrument>, <spread>) tuples.
    @classmethod
    def get_spreads(cls, instruments, since=None):
        #log.write ('"oanda.py" get_spreads(): Entering. Retrieving spreads for: ', instruments)
        prices = cls.get_prices(instruments, since)
        if prices != None:
            spreads = {}
            for p in prices['prices']:
                spreads[p['instrument']] = cls.to_pips( p['instrument'], (p['ask'] - p['bid']) )
            return spreads
        else:
            log.write('"oanda.py" get_spreads(): Failed to get prices.')
            sys.exit()

    # Get one spread value
    @classmethod
    def get_spread(cls, instrument, since=None):
        #log.write('"oanda.py" get_spread(): Entering.')
        spreads = cls.get_spreads(instrument, since)
        if spreads != None:
            return spreads[instrument]
        else:
            log.write('"oanda.py" get_spread(): Failed to get spreads.')
            sys.exit()

    # Buy an instrument
    # Returns: dict or None
    @classmethod
    def place_order(cls, in_order):
        #log.write('"oanda.py" place_order(): Entering.')
        log.write ('"oanda.py" place_order(): Placing order...')
        request_args = {}
        request_args['instrument'] = in_order.instrument
        request_args['units'] = in_order.units
        request_args['side'] = in_order.side
        request_args['type'] = in_order.order_type
        request_args['expiry'] = in_order.expiry
        request_args['price'] = in_order.price
        if in_order.lower_bound != None:
            request_args['lowerBound'] = in_order.lower_bound
        if in_order.upper_bound != None:
            request_args['upperBound'] = in_order.upper_bound
        if in_order.stop_loss != None:
            request_args['stopLoss'] = in_order.stop_loss
        if in_order.take_profit != None:
            request_args['takeProfit'] = in_order.take_profit
        if in_order.trailing_stop != None:
            request_args['trailingStop'] = in_order.trailing_stop
        data = urllib.parse.urlencode(request_args)
        data = cls.stob(data) # convert string to bytes
        result = cls.fetch( cls.get_rest_url() + '/v1/accounts/' + cls.get_account_id_primary() + '/orders', None, data)
        if result == None:
            log.write('"oanda.py" place_order(): Failed to place order.')
            sys.exit()
        else:
            return result

    # Is the market open?
    # Returns: Boolean
    # instrument        = one currency pair formatted like this: 'EUR_USD' 
    @classmethod
    def is_market_open(cls, instrument):
        #log.write('"oanda.py" is_market_open(): Entering.')
        prices = cls.get_prices( instrument )
        if prices['prices'][0]['status'] == 'halted':
            return False
        else:
            return True

    # Get transaction history
    # Returns: dict or None
    @classmethod
    def get_transaction_history(cls, maxId=None, minId=None, count=None, instrument=None, ids=None):
        return trans

    # Go through all transactions that have occurred since a given order, and see if any of those
    # transactions have closed or canceled the order.
    # Returns: Boolean or None
    @classmethod
    def is_trade_closed(cls, transaction_id):
        if transaction_id in cls.closed_trades:
            return True
        else:
            return False

    # Get info about all open trades
    # Returns: dict or None
    @classmethod
    def get_trades(cls):
        #log.write('"oanda.py" get_trades(): Entering.')
        info = cls.fetch(\
             cls.get_rest_url() + '/v1/accounts/' + str(cls.get_account_id_primary()) + '/trades/' )
        if info == None:
            return None
        else:
            return info

    # Get info about a particular trade
    # Returns: dict or None
    @classmethod
    def get_trade(cls, trade_id):
        #log.write('"oanda.py" get_trade(): Entering.')
        info = cls.fetch(\
             cls.get_rest_url() + '/v1/accounts/' + str(cls.get_account_id_primary()) + '/trades/' + str(trade_id) )
        if info != None:
            return info
        else:
            # Apparently the Oanda REST API returns a 404 error if the trade has closed, so don't freak out here.
            log.write('"oanda.py" get_trade(): Failed to get trade info for trade with ID ', trade_id, '.')
            return None

    # Get order info
    # Returns: dict or None
    @classmethod
    def get_order_info(cls, order_id):
        #log.write('"oanda.py" get_order_info(): Entering.')
        response = cls.fetch(\
             cls.get_rest_url() + '/v1/accounts/' + str(cls.get_account_id_primary()) + '/orders/' + str(order_id) )
        if response != None:
            return response
        else:
            log.write('"oanda.py" get_order_info(): Failed to get order info.')
            sys.exit()
        
    # Modify an existing order
    # Returns: dict or None
    @classmethod
    def modify_order(cls, in_order_id, in_units=0, in_price=0, in_expiry=0, in_lower_bound=0,\
        in_upper_bound=0, in_stop_loss=0, in_take_profit=0, in_trailing_stop=0):
        #log.write('"oanda.py" modify_order(): Entering.')

        request_args = {}
        if in_units != 0:
            request_args['units'] = in_units
        if in_price != 0:
            request_args['price'] = in_price
        if in_expiry != 0:
            request_args['expiry'] = in_expiry
        if in_lower_bound != 0:
            request_args['lowerBound'] = in_lower_bound
        if in_upper_bound != 0:
            request_args['upperBound'] = in_upper_bound
        if in_stop_loss != 0:
            request_args['stopLoss'] = in_stop_loss
        if in_take_profit != 0:
            request_args['takeProfit'] = in_take_profit
        if in_trailing_stop != 0:
            request_args['trailingStop'] = in_trailing_stop

        data = urllib.parse.urlencode(request_args)
        data = cls.stob(data) # convert string to bytes

        response = cls.fetch( cls.get_rest_url() + '/v1/accounts/' + str(cls.get_account_id_primary()) + '/orders/'\
            + str(in_order_id), None, data, None, False, 'PATCH' )
        if response != None:
            return response
        else:
            log.write('"oanda.py" modify_order(): Failed to modify order.')
            sys.exit()

    # Modify an existing trade
    # Returns: dict or None
    @classmethod
    def modify_trade(cls, in_trade_id, in_stop_loss=0, in_take_profit=0, in_trailing_stop=0):
        #log.write('"oanda.py" modify_trade(): Entering.')
        request_args = {}
        if in_stop_loss != 0:
            request_args['stopLoss'] = in_stop_loss
        if in_take_profit != 0:
            request_args['takeProfit'] = in_take_profit
        if in_trailing_stop != 0:
            request_args['trailingStop'] = in_trailing_stop
        data = urllib.parse.urlencode(request_args)
        data = cls.stob(data) # convert string to bytes
    
        response = cls.fetch( cls.get_rest_url() + '/v1/accounts/' + str(cls.get_account_id_primary()) + '/trades/'\
            + str(in_trade_id), None, data, None, False, 'PATCH' )
        if response != None:
            return response
        else:
            log.write('"oanda.py" modify_trade(): Failed to modify trade.')
            return None

    #
    def get_next_candle(cls):
        
        # check if any orders need to be placed
        #for o in cls.open_orders:

        # check if any trades need to be closed (check SL/TP)
        for t in self.open_trades:
            pass

    # If there is not a MySQL candle iterator for the given instrument, create one.
    # `instrument` is one string such as "USD_JPY".
    # returns: None
    def append_instrument(cls, instrument):
        if not instrument in cls.candles:
            blah = mysql(blah)
            candles[instrument] = TODO

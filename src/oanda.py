# -*- coding: utf-8 -*-

"""
File            oanda.py
Python ver.     3.4
Description     Python module for Oanda fxTrade REST API.
                http://developer.oanda.com/
                Class methods are used becuase only one instance of the Oanda
                class is ever needed.
"""

#--------------------------
import configparser
import gzip
import json
import sys
import time                 # for sleep()
import traceback
import urllib.request
import urllib.error
import zlib
#--------------------------
from currency_pair_conversions import *
from data_conversions import *
from log import Log
from trade import *
#--------------------------

class Oanda():
    cfg = configparser.ConfigParser()
    cfg.read('config_nonsecure.cfg')
    config_path = cfg['config_secure']['path']
    cfg.read(config_path)
    practice = cfg['trading']['practice']

    account_id_primary = 0


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
        cfg = configparser.ConfigParser()
        cfg.read('config_nonsecure.cfg')
        config_path = cfg['config_secure']['path']
        cfg.read(config_path)
        if Oanda.practice:
            token = cfg['oanda']['token_practice']
        else:
            token = cfg['oanda']['token']
        if token == None:
            Log.write('"oanda.py" get_auth_key(): Failed to read token.')
            sys.exit()
        else:
            return token


    # Which REST API to use?
    @classmethod
    def get_rest_url(cls):
        #Log.write('"oanda.py" get_rest_url(): Entering.')
        if cls.practice:
            return 'https://api-fxpractice.oanda.com'
        else:
            return 'https://api-fxtrade.oanda.com'
     

    @classmethod
    def fetch(cls, in_url, in_headers={}, in_data=None, in_origin_req_host=None,
    in_unverifiable=False, in_method=None):
        """
        Helpful function for accessing Oanda's REST API
        Returns: dict or None.
        """
        Log.write('"oanda.py" fetch(): ***** beginning ************************\\' )
        Log.write('"oanda.py" fetch(): Parameters:\n\
            in_url: {0}\n\
            in_headers: {1}\n\
            in_data: {2}\n\
            origin_req_host: {3}\n\
            unverifiable: {4}\n\
            method: {5}\n\
            '.format(in_url, in_headers, btos(in_data), in_origin_req_host,
            in_unverifiable, in_method))
        # If headers are specified, use those.
        if in_headers == {}:
            headers = {\
            'Authorization': 'Bearer ' + cls.get_auth_key(),\
            'Content-Type': 'application/x-www-form-urlencoded',\
            'Accept-Encoding': 'gzip, deflate'}
        else:
            headers = in_headers
        # send request
        req = urllib.request.Request(in_url, in_data, headers, in_origin_req_host, in_unverifiable, in_method)
        response = None
        # The Oanda REST API returns 404 error if you try to get trade info for a closed trade,
        #   so don't freak out if that happens.
        try:
            response = urllib.request.urlopen( req )
            # Check the response code.
            response_code = response.getcode()
            if response_code == 404:
                Log.write('"oanda.py" fetch(): Response code ', response_code)
            elif response_code == 415:
                # unsupported media type (content-encoding)
                Log.write('"oanda.py" fetch(): Response code 415: Unsupported media type')
            elif response_code != 200:
                Log.write('"oanda.py" fetch(): Response code was not 200.')
            Log.write('"oanda.py" fetch(): RESPONSE CODE: ', response_code)
            # Other stuff
            Log.write('"oanda.py" fetch(): RESPONSE URL:\n    ', response.geturl())
            resp_info = response.info()
            Log.write( '"oanda.py" fetch(): RESPONSE INFO:\n', resp_info )
            # Get the response data.
            """
            response.info() is email.message_from_string(); it needs to be
            # cast to a string.
            """
            resp_data = ''
            # See if the response data is encoded.
            header = response.getheader('Content-Encoding')
            if header != None:
                if header.strip().startswith('gzip'):
                    resp_data = btos(gzip.decompress(response.read()))
                else:
                    if header.strip().startswith('deflate'):
                        resp_data = btos( zlib.decompress( response.read() ) )
                    else:
                        resp_data = btos( response.read() )
            else:
                resp_data = btos(response.read())
            Log.write('"oanda.py" fetch(): RESPONSE PAYLOAD:\n', resp_data, '\n')
            # Parse the JSON from Oanda into a dict, then return it.
            resp_data_str = json.loads(resp_data)
            Log.write('"oanda.py" fetch(): ***** ending ***************************/' )
            return resp_data_str
        except (urllib.error.URLError):
            """
            sys.last_traceback
            https://docs.python.org/3.4/library/traceback.html
            """
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.write('"oanda.py" fetch(): URLError: ', exc_type)
            Log.write('"oanda.py" fetch(): EXC INFO: ', exc_value)
            Log.write('"oanda.py" fetch(): TRACEBACK:\n', traceback.print_exc(), '\n')
            return None
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.write('"oanda.py" fetch(): Exception: ', exc_type)
            Log.write('"oanda.py" fetch(): EXC INFO: ', exc_value)
            Log.write('"oanda.py" fetch(): TRACEBACK:\n', traceback.print_exc(), '\n')
            return None


    @classmethod
    def get_accounts(cls):
        """
        Get list of accounts
        Returns: dict or None
        """
        Log.write('"oanda.py" get_accounts(): Entering.')
        accounts = cls.fetch(cls.get_rest_url() + '/v1/accounts')
        if accounts != None:
            return accounts
        else:
            Log.write('"oanda.py" get_accounts(): Failed to get accounts.')
            sys.exit()

    
    @classmethod
    def get_account_id_primary(cls):
        """
        Get ID of account to trade with.
        Returns: String
        """
        Log.write('"oanda.py" get_account_id_primary(): Entering.')
        if cls.account_id_primary == 0: # if it hasn't been defined yet
            #Log.write('"oanda.py" get_account_id_primary(): Entering.')
            accounts = cls.get_accounts()
            if accounts != None:
                for a in accounts['accounts']:
                    if a['accountName'] == 'Primary':
                        cls.account_id_primary = str(a['accountId'])
                        return cls.account_id_primary 
            Log.write('"oanda.py" get_account_id_primary(): Failed to get accounts.')
            sys.exit()
        else: # reduce overhead
            return cls.account_id_primary


    # Get account info for a given account ID
    # Returns: dict or None 
    @classmethod
    def get_account(cls, account_id):
        Log.write('"oanda.py" get_account(): Entering.')
        account = cls.fetch(cls.get_rest_url() + '/v1/accounts/' + account_id)
        if account != None:
            return account
        else:
            Log.write('"oanda.py" get_account(): Failed to get account.')
            sys.exit()

    # Get list of open positions
    # Returns: dict or None 
    @classmethod
    def get_positions(cls, account_id):
        #Log.write('"oanda.py" get_positions(): Entering.')
        pos = cls.fetch( cls.get_rest_url() + '/v1/accounts/' + account_id + '/positions')
        if pos != None:
            return pos
        else:
            Log.write('"oanda.py" get_positions(): Failed to get positions.')
            sys.exit()


    # Get number of positions for a given account ID
    # Returns: Integer
    @classmethod
    def get_num_of_positions(cls, account_id):
        #Log.write('"oanda.py" get_num_of_positions(): Entering.')
        positions = cls.get_positions(account_id)
        if positions != None:
            return len(positions['positions'])
        else:
            Log.write('"oanda.py" get_num_of_positions(): Failed to get positions.')
            sys.exit()


    # Get account balance for a given account ID
    # Returns: Decimal number
    @classmethod
    def get_balance(cls, account_id):
        #Log.write('"oanda.py" get_balance(): Entering.')
        account = cls.get_account(account_id)
        if account != None:
            return account['balance']
        else:
            Log.write('"oanda.py" get_balance(): Failed to get account.')
            sys.exit()


    # Fetch live prices for specified instruments that are available on the OANDA platform.
    # Returns: dict or None
    # `instruments' argument must be URL encoded comma-separated, e.g. USD_JPY%2CEUR_USD
    @classmethod
    def get_prices(cls, instruments, since=None):
        #Log.write('"oanda.py" get_prices(): Entering.')
        url_args = '?instruments=' + instruments
        if since != None:
            url_args += '&since=' + since
        prices = cls.fetch( cls.get_rest_url() + '/v1/prices' + url_args )
        if prices != None:
            return prices
        else:
            Log.write('"oanda.py" get_prices(): Failed to get prices.')
            sys.exit()


    # Get one ask price
    # Returns: Decimal or None
    # TODO: check instrument string being passed in
    @classmethod
    def get_ask(cls, instrument, since=None):
        #Log.write('"oanda.py" get_ask(): Entering.')
        prices = cls.get_prices(instrument, since)
        if prices != None:
            for p in prices['prices']:
                if p['instrument'] == instrument:
                    return float(p['ask'])
        else:
            Log.write('"oanda.py" get_ask(): Failed to get prices.')
            sys.exit()


    # Get one bid price
    # Returns: Decimal or None
    @classmethod
    def get_bid(cls, instrument, since=None):
        #Log.write('"oanda.py" get_bid(): Entering. Getting bid of ', instrument, '.')
        prices = cls.get_prices(instrument, since)
        if prices != None:
            for p in prices['prices']:
                if p['instrument'] == instrument:
                    return float(p['bid'])
        else:
            Log.write('"oanda.py" get_bid(): Failed to get prices.')
            sys.exit()


    @classmethod
    def get_spreads(cls, instruments, since=None):
        """
        Get spread, in pips, for given currency pairs (e.g. 'USD_JPY%2CEUR_USD')

        Sample return value:
        [
            {
                "instrument":"USD_JPY",
                "time":"2013-06-21T17:49:02.475381Z",
                "spread":3.2,
                "status":"halted"           // Oanda doesn't include this if
                                            // the instrument isn't halted,
                                            // but I will always include it.
            },
            {
                "instrument":"USD_CAD",
                "time":"2013-06-21T17:49:02.475381Z",
                "spread":4.4,
                "status":""
            }
        ]
        """
        Log.write ('"oanda.py" get_spreads(): Retrieving spreads for {}'.format(instruments))
        prices = cls.get_prices(instruments, since)
        if prices != None:
            spreads = []
            for p in prices['prices']:
                # Since Oanda doesn't always include status, force it in.
                if 'status' not in p:
                    p['status'] = ""
                #spreads[p['instrument']] = price_to_pips( p['instrument'], (p['ask'] - p['bid']) )
                spreads.append(
                    {
                        "instrument":p['instrument'],
                        "time":p['time'],
                        "spread":price_to_pips(p['instrument'], (p['ask'] - p['bid'])),
                        "status":p['status']
                    }
                )
            Log.write('"oanda.py" get_spreads(): Spreads:\n{}\n'
                .format(spreads))
            return spreads
        else:
            Log.write('"oanda.py" get_spreads(): Failed to get prices.')
            sys.exit()


    @classmethod
    def place_order(cls, in_order):
        """
        Place an order.
        Returns: information about the order (and related trade)

        If I place a trade that reduces another trade to closing, then I get a
        200 Code and information about the trade that closed. I.e. I don't get
        info about an opened trade.
        """
        Log.write ('"oanda.py" place_order(): Placing order...')
        request_args = {}
        if in_order.instrument != None:
            request_args['instrument'] = in_order.instrument
        if in_order.units != None:
            request_args['units'] = in_order.units
        if in_order.side != None:
            request_args['side'] = in_order.side
        if in_order.order_type != None:
            request_args['type'] = in_order.order_type
        if in_order.expiry != None:
            request_args['expiry'] = in_order.expiry
        if in_order.price != None:
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
        # url-encode, then convert to bytes
        data = stob(urllib.parse.urlencode(request_args))
        result = cls.fetch(
            in_url="{}/v1/accounts/{}/orders".format(
                cls.get_rest_url(),
                cls.get_account_id_primary()
            ),
            in_data=data,
            in_method='POST'
            )
        if result == None:
            Log.write('"oanda.py" place_order(): Failed to place order.')
            Log.write('"oanda.py" place_order(): Aborting.')
            sys.exit()
        else:
            Log.write ('"oanda.py" place_order(): Order successfully placed.')
            return result


    @classmethod
    def is_market_open(cls, instrument='USD_JPY'):
        """
        # Is the market open?
        # Returns: Boolean
        # instrument        = one currency pair formatted like this: 'EUR_USD' 
        """
        #Log.write('"oanda.py" is_market_open(): Entering.')
        prices = cls.get_prices( instrument )
        if prices['prices'][0]['status'] == 'halted':
            return False
        else:
            return True


    # Get transaction history
    # Returns: dict or None
    @classmethod
    def get_transaction_history(cls, maxId=None, minId=None, count=None, instrument=None, ids=None):
        #Log.write('"oanda.py" get_transaction_history(): Entering.')

        args = ''
        if not maxId == None:
            if args != '':
                args = args + '&'
            args = args + 'maxId=' + str(maxId)
        if not minId == None:
            if args != '':
                args = args + '&'
            args = args + 'minId=' + str(minId)
        if not count == None:
            if args != '':
                args = args + '&'
            args = args + 'count=' + str(count)
        if not instrument == None:
            if args != '':
                args = args + '&'
            args = args + 'instrument=' + str(instrument)
        if not ids == None:
            if args != '':
                args = args + '&'
            args = args + 'ids=' & str(ids)
        trans = cls.fetch(\
            cls.get_rest_url() + '/v1/accounts/' + cls.get_account_id_primary() + '/transactions?' + args)
        if trans == None:
            sys.exit()
        else:
            return trans


    @classmethod
    def is_trade_closed(cls, transaction_id):
        """
        Go through all transactions that have occurred since a given order, and see if any of those
        transactions have closed or canceled the order.
        Returns:    True if trade is closed; False if not closed.
                    None on error.
        """
        #Log.write('"oanda.py" is_trade_closed(): Entering.')
        # TODO: add a delay to allow time for the transaction history to be updated. 
        num_attempts = 2
        while num_attempts > 0:
            Log.write('"oanda.py" is_trade_closed(): Remaining attempts: ', str(num_attempts))
            trans = cls.get_transaction_history(None, transaction_id)
            if trans == None:
                Log.write('"oanda.py" is_trade_closed(): Failed to get transaction history.')
                sys.exit()
            else:
                for t in trans['transactions']:
                    if t['type'] == 'TRADE_CLOSE':
                        if t['tradeId'] == transaction_id:
                            Log.write('"oanda.py" is_trade_closed(): TRADE_CLOSE')
                            return True
                    if t['type'] == 'MIGRATE_TRADE_CLOSE':
                        if t['tradeId'] == transaction_id:
                            Log.write('"oanda.py" is_trade_closed(): MIGRATE_TRADE_CLOSED')
                            return True
                    if t['type'] == 'STOP_LOSS_FILLED':
                        if t['tradeId'] == transaction_id:
                            Log.write('"oanda.py" is_trade_closed(): STOP_LOSS_FILLED')
                            return True
                    if t['type'] == 'TAKE_PROFIT_FILLED':
                        if t['tradeId'] == transaction_id:
                            Log.write('"oanda.py" is_trade_closed(): TAKE_PROFIT_FILLED')
                            return True
                    if t['type'] == 'TRAILING_STOP_FILLED':
                        if t['tradeId'] == transaction_id:
                            Log.write('"oanda.py" is_trade_closed(): TRAILING_STOP_FILLED')
                            return True
                    if t['type'] == 'MARGIN_CLOSEOUT':
                        if t['tradeId'] == transaction_id:
                            Log.write('"oanda.py" is_trade_closed(): MARGIN_CLOSEOUT')
                            return True
            num_attempts = num_attempts - 1
            time.sleep(1)
        Log.write('"oanda.py" is_trade_closed(): Unable to locate trade. Assuming trade is still open.')
        return False


    # Get info about all open trades
    # Returns: instance of <trades>.
    @classmethod
    def get_trades(cls):
        Log.write('"oanda.py" get_trades(): Entering.')
        trades_oanda = cls.fetch(\
            '{}/v1/accounts/{}/trades/'.format(
                cls.get_rest_url(),
                str(cls.get_account_id_primary())
            )
        )
        if trades_oanda == None:
            Log.write('"oanda.py" get_trades(): Failed to get trades from Oanda.')
            raise Exception
        else:
            ts = Trades()
            for t in trades_oanda['trades']: 
                # format into a <Trade>
                ts.append(Trade(t['id'], t['instrument']))
            return ts


    @classmethod
    def get_trade(cls, trade_id):
        """
        Get info about a particular trade.
        """
        Log.write('"oanda.py" get_trade(): Entering.')
        t = cls.fetch(
            '{}/v1/accounts/{}/trades/{}'.format(
                cls.get_rest_url(),
                str(cls.get_account_id_primary()),
                str(trade_id)
            )
        )
        if t != None:
            return Trade(t['id'], t['instrument'])
        else:
            # Apparently the Oanda REST API returns a 404 error if the trade has closed, so don't freak out here.
            Log.write('"oanda.py" get_trade(): Failed to get trade info for trade with ID ', trade_id, '.')
            return None

    # Get order info
    # Returns: dict or None
    @classmethod
    def get_order_info(cls, order_id):
        #Log.write('"oanda.py" get_order_info(): Entering.')
        response = cls.fetch(\
             cls.get_rest_url() + '/v1/accounts/' + str(cls.get_account_id_primary()) + '/orders/' + str(order_id) )
        if response != None:
            return response
        else:
            Log.write('"oanda.py" get_order_info(): Failed to get order info.')
            sys.exit()
        
    # Modify an existing order
    # Returns: dict or None
    @classmethod
    def modify_order(cls, in_order_id, in_units=0, in_price=0, in_expiry=0, in_lower_bound=0,\
        in_upper_bound=0, in_stop_loss=0, in_take_profit=0, in_trailing_stop=0):
        #Log.write('"oanda.py" modify_order(): Entering.')

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
        data = stob(data) # convert string to bytes

        response = cls.fetch(cls.get_rest_url() + '/v1/accounts/'\
            + str(cls.get_account_id_primary()) + '/orders/'\
            + str(in_order_id), None, data, None, False, 'PATCH')
        if response != None:
            return response
        else:
            Log.write('"oanda.py" modify_order(): Failed to modify order.')
            sys.exit()

    # Modify an existing trade
    # Returns: dict or None
    @classmethod
    def modify_trade(cls, in_trade_id, in_stop_loss=0, in_take_profit=0, in_trailing_stop=0):
        #Log.write('"oanda.py" modify_trade(): Entering.')
        request_args = {}
        if in_stop_loss != 0:
            request_args['stopLoss'] = in_stop_loss
        if in_take_profit != 0:
            request_args['takeProfit'] = in_take_profit
        if in_trailing_stop != 0:
            request_args['trailingStop'] = in_trailing_stop
        data = urllib.parse.urlencode(request_args)
        data = stob(data) # convert string to bytes
    
        response = cls.fetch( cls.get_rest_url() + '/v1/accounts/'\
            + str(cls.get_account_id_primary()) + '/trades/'\
            + str(in_trade_id), None, data, None, False, 'PATCH' )
        if response != None:
            return response
        else:
            Log.write('"oanda.py" modify_trade(): Failed to modify trade.')
            return None



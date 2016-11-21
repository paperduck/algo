# oanda.py
# Python module for Oanda fxTrade REST API
# Python 3.4

#--------------------------
import json
import sys
#import time         # for sleep()
import urllib.request
import urllib.error
#--------------------------
import log as loggy
import order
#--------------------------

# static class
class oanda():
    
    def __init__(self, in_practice = True):
        self.practice = in_practice
        self.pip_factors = {'AUD_CAD':10000, 'AUD_CHF':10000, 'AUD_HKD':10000, 'AUD_JPY':100, 'USD_JPY': 100}
        self.log = loggy.log(True)
        self.account_id_primary = 0

    # Get authorization key.
    # Oanda was returning a '400 Bad Request' error 4 out of 5 times
    #   until I removed the trailing '\n' from the string
    #   returned by f.readline().
    def get_auth_key(self):
        #self.log.write('"oanda.py" get_auth_key(): Entering.')
        if self.practice:
            with open('/home/user/raid/documents/oanda_practice_token.txt', 'r') as f:
                auth = f.readline()
                auth = auth.rstrip()
                f.close()
            return auth
        else:
            with open('/home/user/raid/documents/oanda_token.txt', 'r') as f:
                auth = f.readline()
                auth = auth.rstrip()
                f.close()
            return auth

    # Which REST API to use?
    def get_rest_url(self):
        #self.log.write('"oanda.py" get_rest_url(): Entering.')
        if self.practice:
            return 'https://api-fxpractice.oanda.com'
        else:
            return 'https://api-fxtrade.oanda.com'
     
    # Decode bytes to string using UTF8.
    # Parameter `b' is assumed to have type of `bytes'.
    def btos(self, b):
        #self.log.write('"oanda.py" btos(): Entering.')
        return b.decode('utf_8')
    #
    def stob(self, s):
        #self.log.write('"oanda.py" stob(): Entering.')
        return s.encode('utf_8')

    # Helpful function for accessing Oanda's REST API
    # Returns JSON as a string, or None.
    # Prints error info to stdout.
    def fetch(self, in_url, in_headers=None, in_data=None, origin_req_host=None, unverifiable=False, method=None):
        #self.log.write('"oanda.py" fetch(): Entering.')
        # headers; if anything is specified, then let that overwrite default.
        if in_headers == None:
            headers = {'Authorization': 'Bearer ' + self.get_auth_key(),\
            'Content-Type': 'application/x-www-form-urlencoded'}
        else:
            headers = in_headers
        '''
        self.log.write ('"oanda.py" fetch():     headers: ', headers)
        # url
        #self.log.write ('"oanda.py" oanda.fetch():     url:  ', in_url)
        # data
        if in_data != None:
            self.log.write('"oanda.py" fetch():     data: \n\n', self.btos(in_data), '\n')
        else:
            self.log.write('"oanda.py" fetch():     data: None')
        # log method
        self.log.write('"oanda.py" fetch():     method: ', method, '.')
        '''
        # send request
        req = urllib.request.Request(in_url, in_data, headers, origin_req_host, unverifiable, method)
        response = None
        # The Oanda REST API returns 404 error if you try to get trade info for a closed trade,
        #   so don't freak out if that happens.
        try:
            response = urllib.request.urlopen(req)
            #self.log.write('"oanda.py" in fetch(): RESPONSE URL: ', response.geturl())
            #self.log.write('"oanda.py" in fetch(): RESPONSE INFO:', response.info())
            #self.log.write('"oanda.py" in fetch(): RESPONSE CODE: ', response.getcode())
            response_data = self.btos(response.read())
            #self.log.write('"oanda.py" fetch(): RESPONSE:\n', response_data, '\n')
            response_data_str = json.loads(response_data)
            return response_data_str
        except (urllib.error.URLError):
            self.log.write('"oanda.py" fetch(): URLError: ', sys.exc_info()[0])
            self.log.write('"oanda.py" fetch(): EXC INFO: ', sys.exc_info()[1])
            #self.log.write('"oanda.py" fetch(): Exiting program.')
            #sys.exit()
            return None
        except:
            self.log.write('"oanda.py" fetch(): other error:', sys.exc_info()[0])
            #self.log.write('"oanda.py" fetch(): Exiting program.')
            #sys.exit()
            return None

    # Get list of accounts
    # Returns: dict or None
    def get_accounts(self):
        #self.log.write('"oanda.py" in get_accounts(): Entering.')
        accounts = self.fetch(self.get_rest_url() + '/v1/accounts')
        if accounts != None:
            return accounts
        else:
            log.write('"oanda.py" in get_accounts(): Failed to get accounts.')
            sys.exit()
            return None
    
    # Get ID of account to trade with.
    # Returns: String
    def get_account_id_primary(self):
        if self.account_id_primary == 0: # if it hasn't been defined yet
            #self.log.write('"oanda.py" get_account_id_primary(): Entering.')
            accounts = self.get_accounts()
            if accounts != None:
                for a in accounts['accounts']:
                    if a['accountName'] == 'Primary':
                        self.account_id_primary = str(a['accountId'])
                        return self.account_id_primary 
            self.log.write('"oanda.py" in get_account_id_primary(): Failed to get accounts.')
            sys.exit()
            #return None
        else: # reduce overhead
            return self.account_id_primary

    # Get account info for a given account ID
    # Returns: dict or None 
    def get_account(self, account_id):
        #self.log.write('"oanda.py" get_account(): Entering.')
        account = self.fetch(get_rest_url() + '/v1/accounts/' + account_id)
        if account != None:
            return account
        else:
            self.log.write('"oanda.py" in get_account(): Failed to get account.')
            sys.exit()
            return None

    # Get list of open positions
    # Returns: dict or None 
    def get_positions(self, account_id):
        #self.log.write('"oanda.py" get_positions(): Entering.')
        pos = self.fetch( get_rest_url() + '/v1/accounts/' + account_id + '/positions')
        if pos != None:
            return pos
        else:
            self.log.write('"oanda.py" in get_positions(): Failed to get positions.')
            sys.exit()
            return None

    # Get number of positions for a give account ID
    # Returns: Number
    def get_num_of_positions(self, account_id):
        #self.log.write('"oanda.py" get_num_of_positions(): Entering.')
        positions = get_positions(account_id)
        if positions != None:
            return len(positions['positions'])
        else:
            self.log.write('"oanda.py" in get_num_of_positions(): Failed to get positions.')
            sys.exit()
            return None

    # Get account balance for a given account ID
    # Returns: Decimal number
    def get_balance(self, account_id):
        #self.log.write('"oanda.py" get_balance(): Entering.')
        account = self.get_account(account_id)
        if account != None:
            return account['balance']
        else:
            self.log.write('"oanda.py" in get_balance(): Failed to get account.')
            sys.exit()
            return None

    # Fetch live prices for specified instruments that are available on the OANDA platform.
    # Returns: dict or None
    # `instruments' argument must be URL encoded comma-separated, e.g. USD_JPY%2CEUR_USD
    def get_prices(self, instruments, since=None):
        #self.log.write('"oanda.py" get_prices(): Entering.')
        url_args = '?instruments=' + instruments
        if since != None:
            url_args += '&since=' + since
        prices = self.fetch( self.get_rest_url() + '/v1/prices' + url_args )
        if prices != None:
            return prices
        else:
            self.log.write('"oanda.py" in get_prices(): Failed to get prices.')
            sys.exit()
            return None

    # Get one ask price
    # Returns: Decimal or None
    def get_ask(self, instrument, since=None):
        #self.log.write('"oanda.py" get_ask(): Entering.')
        prices = self.get_prices(instrument, since)
        if prices != None:
            for p in prices['prices']:
                if p['instrument'] == instrument:
                    return float(p['ask'])
        else:
            self.log.write('"oanda.py" in get_ask(): Failed to get prices.')
            sys.exit()
            return None

    # Get one bid price
    # Returns: Decimal or None
    def get_bid(self, instrument, since=None):
        #self.log.write('"oanda.py" get_bid(): Entering. Getting bid of ', instrument, '.')
        prices = self.get_prices(instrument, since)
        if prices != None:
            for p in prices['prices']:
                if p['instrument'] == instrument:
                    return float(p['bid'])
        else:
            self.log.write('"oanda.py" in get_bid(): Failed to get prices.')
            sys.exit()
            return None

    # Given an instrument (e.g. 'USD_JPY') and price, convert price to pips
    # Returns: decimal or None
    def to_pips(self, instrument, value):
        #self.log.write('"oanda.py" to_pips(): Entering.')
        if instrument in self.pip_factors:
            return self.pip_factors[instrument] * value
        else:
            return None

    # Get spread, in pips, for given currency pairs (e.g. 'USD_JPY%2CEUR_USD')
    # Returns: dict of (<instrument>, <spread>) tuples.
    def get_spreads(self, instruments, since=None ):
        #self.log.write ('"oanda.py" in get_spreads(): Entering. Retrieving spreads for: ', instruments)
        prices = self.get_prices(instruments, since)
        if prices != None:
            spreads = {}
            for p in prices['prices']:
                spreads[p['instrument']] = self.to_pips( p['instrument'], (p['ask'] - p['bid']) )
            return spreads
        else:
            self.log.write('"oanda.py" in get_spreads(): Failed to get prices.')
            sys.exit()
            return None

    # Get one spread value
    def get_spread(self, instrument, since=None):
        #self.log.write('"oanda.py" get_spread(): Entering.')
        spreads = self.get_spreads(instrument, since)
        if spreads != None:
            return spreads[instrument]
        else:
            self.log.write('"oanda.py" in get_spread(): Failed to get spreads.')
            sys.exit()
            return None

    # Buy an instrument
    # Returns: dict or None
    def place_order(self, in_order):
        #self.log.write('"oanda.py" place_order(): Entering.')
        self.log.write ('"oanda.py" in place_order(): Placing order...')
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
        data = self.stob(data) # convert string to bytes
        result = self.fetch( self.get_rest_url() + '/v1/accounts/' + self.get_account_id_primary() + '/orders', None, data)
        if result != None:
            return result
        else:
            sys.exit()
            return None

    # Is the market open?
    # Returns: Boolean
    # instrument        = one currency pair formatted like this: 'EUR_USD' 
    def is_market_open(self, instrument):
        #self.log.write('"oanda.py" is_market_open(): Entering.')
        prices = self.get_prices( instrument )
        if prices['prices'][0]['status'] == 'halted':
            return False
        else:
            return True

    # Get transaction history
    # Returns: dict or None
    def get_transaction_history(self, maxId=None, minId=None, count=None, instrument=None, ids=None):
        #self.log.write('"oanda.py" get_transaction_history(): Entering.')

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
        trans = self.fetch(\
            self.get_rest_url() + '/v1/accounts/' + self.get_account_id_primary() + '/transactions?' + args)
        if trans != None:
            return trans
        else:
            return None

    # Go through all transactions that have occurred since a given order, and see if any of those
    # transactions have closed or canceled the order.
    # Returns: Boolean or None
    def is_trade_closed(self, transaction_id):
        #self.log.write('"oanda.py" is_trade_closed(): Entering.')
        trans = self.get_transaction_history(None, transaction_id)
        if trans == None:
            self.log.write('"oanda.py" is_trade_closed(): Failed to get transaction history.')
            sys.exit()
        else:
            for t in trans['transactions']:
                if t['type'] in ['TRADE_CLOSE', 'MIGRATE_TRADE_CLOSE', 'STOP_LOSS_FILLED', 'TAKE_PROFIT_FILLED', \
                'TRAILING_STOP_FILLED', 'MARGIN_CLOSEOUT']:
                    if t['tradeId'] == transaction_id:
                        return True
            return False

    # Get trade info
    # Returns: dict or None
    def get_trade_info(self, trade_id):
        #self.log.write('"oanda.py" get_trade_info(): Entering.')
        info = self.fetch(\
             self.get_rest_url() + '/v1/accounts/' + str(self.get_account_id_primary()) + '/trades/' + str(trade_id) )
        if info != None:
            return info
        else:
            # Apparently the Oanda REST API returns a 404 error if the trade has closed, so don't freak out here.
            self.log.write('"oanda.py" in get_trade_info(): Failed to get trade info for trade with ID ', trade_id, '.')
            return None

    # Get order info
    # Returns: dict or None
    def get_order_info(self, order_id):
        #self.log.write('"oanda.py" get_order_info(): Entering.')
        response = self.fetch(\
             self.get_rest_url() + '/v1/accounts/' + str(self.get_account_id_primary()) + '/orders/' + str(order_id) )
        if response != None:
            return response
        else:
            self.log.write('"oanda.py" in get_order_info(): Failed to get order info.')
            sys.exit()
            return None
        
    # Modify an existing order
    # Returns: dict or None
    def modify_order(self, in_order_id, in_units=0, in_price=0, in_expiry=0, in_lower_bound=0,\
        in_upper_bound=0, in_stop_loss=0, in_take_profit=0, in_trailing_stop=0):
        #self.log.write('"oanda.py" modify_order(): Entering.')

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
        data = self.stob(data) # convert string to bytes

        response = self.fetch( self.get_rest_url() + '/v1/accounts/' + str(self.get_account_id_primary()) + '/orders/'\
            + str(in_order_id), None, data, None, False, 'PATCH' )
        if response != None:
            return response
        else:
            log.write('"oanda.py" in modify_order(): Failed to modify order.')
            sys.exit()
            return None

    # Modify an existing trade
    # Returns: dict or None
    def modify_trade(self, in_trade_id, in_stop_loss=0, in_take_profit=0, in_trailing_stop=0):
        #self.log.write('"oanda.py" in modify_trade(): Entering.')
        request_args = {}
        if in_stop_loss != 0:
            request_args['stopLoss'] = in_stop_loss
        if in_take_profit != 0:
            request_args['takeProfit'] = in_take_profit
        if in_trailing_stop != 0:
            request_args['trailingStop'] = in_trailing_stop
        data = urllib.parse.urlencode(request_args)
        data = self.stob(data) # convert string to bytes
    
        response = self.fetch( self.get_rest_url() + '/v1/accounts/' + str(self.get_account_id_primary()) + '/trades/'\
            + str(in_trade_id), None, data, None, False, 'PATCH' )
        if response != None:
            return response
        else:
            self.log.write('"oanda.py" in modify_trade(): Failed to modify trade.')
            sys.exit()
            return None



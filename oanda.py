# oanda.py
# Python module for Oanda fxTrade REST API
# Python 3.4

#--------------------------
import sys
import urllib.request
import urllib.error
#import time         # for sleep()
#from jq import jq
import json
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

    # Get authorization key.
    # Oanda was returning a '400 Bad Request' error 4 out of 5 times
    #   until I removed the trailing '\n' from the string
    #   returned by f.readline().
    def get_auth_key(self):
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
        if self.practice:
            return 'https://api-fxpractice.oanda.com'
        else:
            return 'https://api-fxtrade.oanda.com'
     
    # Decode bytes to string using UTF8.
    # Parameter `b' is assumed to have type of `bytes'.
    def btos(self, b):
        return b.decode('utf_8')
    #
    def stob(self, s):
        return s.encode('utf_8')

    # Helpful function for accessing Oanda's REST API
    # Returns JSON as a string, or None.
    # Prints error info to stdout.
    def fetch(self, in_url, in_headers=None, data=None, origin_req_host=None, unverifiable=False, method=None):
        self.log.write ('in oanda.fetch()')
        if in_headers == None:
            headers = {'Authorization': 'Bearer ' + self.get_auth_key(),\
            'Content-Type': 'application/x-www-form-urlencoded'}
        else:
            headers = in_headers
        self.log.write ('url: ', in_url)
        if data != None:
            self.log.write('data: \n\n', self.btos(data), '\n')
        else:
            self.log.write('data: None')
        self.log.write ('headers: ', headers)
        req = urllib.request.Request(in_url, data, headers, origin_req_host, unverifiable, method)
        try:
            response = urllib.request.urlopen(req)
            self.log.write("RESPONSE URL: ", response.geturl())
            self.log.write("RESPONSE INFO:", response.info())
            self.log.write("RESPONSE CODE: ", response.getcode())
            response_data = self.btos(response.read())
            self.log.write('RESPONSE:\n', response_data, '\n')
            return response_data
        except (urllib.error.URLError):
            self.log.write("URLError:", sys.exc_info()[0])
            self.log.write("EXC INFO: ", sys.exc_info()[1])
            self.log.write("Fetch failed.")
            #sys.exit()
            return None
        except:
            self.log.write("other error:", sys.exc_info()[0])
            self.log.write("Fetch failed.")
            #sys.exit()
            return None

    # Get list of accounts
    # Returns: JSON from Oanda
    def get_accounts(self):
        self.log.write('Fetching...')
        return self.fetch(self.get_rest_url() + '/v1/accounts')

    # Get ID of account to trade with. Return it as a string.
    def get_account_id_primary(self):
        json_accounts = self.get_accounts()
        if json_accounts == None:
            return None
        accounts = json.loads(json_accounts)
        account_id_primary = None
        for a in accounts['accounts']:
            if a['accountName'] == 'Primary':
                account_id_primary = str(a['accountId'])
        return account_id_primary

    # Get account info for a given account ID
    # Returns: JSON 
    def get_account(self, account_id):
        self.log.write('oanda.get_account(): Fetching...')
        return self.fetch(get_rest_url() + '/v1/accounts/' + account_id)

    # Get list of open positions
    # Returns: JSON 
    def get_positions(self, account_id):
        self.log.write('oanda.get_positions(): Fetching...')
        return self.fetch( get_rest_url() + '/v1/accounts/' + account_id + '/positions')

    # Get number of positions for a give account ID
    # Returns: Number
    def get_num_of_positions(self, account_id):
        positions = get_positions(account_id)
        position_list = json.loads(positions)
        num_pos = 0
        for p in position_list['positions']:
            num_pos = num_pos + 1
        return num_pos

    # Get account balance for a given account ID
    # Returns: Decimal number
    def get_balance(self, account_id):
        account_info = self.get_account(account_id)
        balance = json.loads(account_info)
        return balance['balance']

    # Fetch live prices for specified instruments that are available on the OANDA platform.
    # Returns: JSON
    # `instruments' argument must be URL encoded comma-separated, e.g. USD_JPY%2CEUR_USD
    def get_prices(self, instruments, since=None):
        url_args = '?instruments=' + instruments
        if since != None:
            url_args += '&since=' + since
        self.log.write('oanda.get_prices(): Fetching...')
        prices = self.fetch( self.get_rest_url() + '/v1/prices' + url_args )
        return prices

    # Get one ask price
    # Returns: Decimal
    def get_ask(self, instrument, since=None):
        prices_json = self.get_prices(instrument, since)
        prices_dict = json.loads(prices_json)
        for p in prices_dict['prices']:
            if p['instrument'] == instrument:
                return float(p['ask'])
        return None

    # Get one bid price
    # Returns: Decimal
    def get_bid(self, instrument, since=None):
        prices_json = self.get_prices(instrument, since)
        prices_dict = json.loads(prices_json)
        for p in prices_dict['prices']:
            if p['instrument'] == instrument:
                return float(p['bid'])
        return None

    # Given an instrument (e.g. 'USD_JPY') and price, convert price to pips
    # Returns: decimal or None
    def to_pips(self, instrument, value):
        if instrument in self.pip_factors:
            return self.pip_factors[instrument] * value
        else:
            return None

    # Get spread, in pips, for given currency pairs (e.g. 'USD_JPY%2CEUR_USD')
    # Returns: dictionary of instruments and decimals
    def get_spreads(self, instruments, since=None ):
        self.log.write ('oanda.get_spreads(): Retrieving spreads for: ', instruments)
        prices_json = self.get_prices(instruments, since)
        spreads = {}
        prices = json.loads(prices_json)
        for p in prices['prices']:
            spreads[p['instrument']] = self.to_pips( p['instrument'], (p['ask'] - p['bid']) )
        return spreads

    # Get one spread value
    def get_spread(self, instrument, since=None):
        spreads = self.get_spreads(instrument, since)
        if instrument in spreads:
            return spreads[instrument]
        else:
            return None

    # Buy an instrument
    # Returns: JSON
    def place_order(self, in_order):
        self.log.write ('Placing order...')
        post_args = {}
        post_args['instrument'] = in_order.instrument
        post_args['units'] = in_order.units
        post_args['side'] = in_order.side
        post_args['type'] = in_order.order_type
        post_args['expiry'] = in_order.expiry
        post_args['price'] = in_order.price
        if in_order.lower_bound != None:
            post_args['lowerBound'] = in_order.lower_bound
        if in_order.upper_bound != None:
            post_args['upperBound'] = in_order.upper_bound
        if in_order.stop_loss != None:
            post_args['stopLoss'] = in_order.stop_loss
        if in_order.take_profit != None:
            post_args['takeProfit'] = in_order.take_profit
        if in_order.trailing_stop != None:
            post_args['trailingStop'] = in_order.trailing_stop
        data = urllib.parse.urlencode(post_args)
        data = self.stob(data) # convert string to bytes
        self.log.write('oanda.place_order(): Fetching...')
        return self.fetch( self.get_rest_url() + '/v1/accounts/' + self.get_account_id_primary() + '/orders', None, data)

    # Is the market open?
    # Returns: Boolean
    # instrument        = one currency pair formatted like this: 'EUR_USD' 
    def is_market_open(self, instrument):
        prices = self.get_prices( instrument )
        prices_str = json.loads(prices)
        if prices_str['prices'][0]['status'] == 'halted':
            return False
        else:
            return True

    # Get transaction history
    # Returns: JSON
    def get_transaction_history(self, maxId=None, minId=None, count=None, instrument=None, ids=None):

        args = ''
        if not maxId == None:
            args = args + 'maxId=' + str(maxId) + '&'
        if not minId == None:
            args = args + 'minId=' + str(minId) + '&'
        if not count == None:
            args = args + 'count=' + str(count) + '&'
        if not instrument == None:
            args = args + 'instrument=' + str(instrument) + '&'
        if not ids == None:
            args = args + 'ids=' & str(ids) + '&'

        return self.fetch( self.get_rest_url() + '/v1/accounts/' + self.get_account_id_primary() + '/transactions?' )

    # Go through all transactions that have occurred since a given order, and see if any of those
    # transactions have closed or canceled the order.
    # Oanda's fxTrade REST API uses the terms "order ID", "transaction ID", and "ticket" interchangeably.
    # Returns: Boolean
    def is_trade_closed(self, transaction_id):
        trans = self.get_transaction_history(None, transaction_id)
        trans_data = json.loads(trans)
        # look at each transaction
        for t in trans_data['transactions']:
            # We only care about transactions that are linked to an order
            if 'orderId' in t:
                # See if this transaction is linked to the order given
                if t['orderId'] == transaction_id:
                    # It's linked, but was the order actually closed?
                    if t['type'] in ['ORDER_CANCEL', 'ORDER_FILLED', 'TRADE_CLOSE', 'MIGRATE_TRADE_CLOSE', 'STOP_LOSS_FILLED',\
                    'TAKE_PROFIT_FILLED', 'TRAILING_STOP_FILLED', 'MARGIN_CLOSEOUT']:
                        return True
        # Didn't find any transactions linked to the given one, so assume the order is still open.
        return False

    #
    # Returns: JSON converted to string
    def get_order_info(self, order_id):
        response = self.fetch(\
             self.get_rest_url() + '/v1/accounts/' + self.get_account_id_primary() + '/orders/' + str(order_id)\
        )
        if response == None:
            self.log.write('"oanda.py" in get_order_info(): fetch() failed.')
            return None
        else:
            return json.loads( response )
        
    # Modify an existing order
    # Returns: JSON as dict
    def modify_order(self, order_number, units=None, price=None, expiry=None, lower_bound=None,\
    upper_bound=None, stop_loss=None, take_profit=None, trailing_stop=None):
        response = self.fetch( self.get_rest_url() + '/v1/accounts/' + get_account_id_primary() + '/orders/'\
            + order_number, None, None, 'PATCH'
        )
        return json.loads( response )




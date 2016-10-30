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

import log
import order

# static class
class oanda():
    
    pip_factors = {'AUD_CAD':10000, 'AUD_CHF':10000, 'AUD_HKD':10000, 'AUD_JPY':100, 'USD_JPY': 100}

    def __init__(self, in_practice = False):
        self.practice = in_practice

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
    def fetch(self, in_url, in_headers=None, data=None):
        log.write_to_log ("\nFetching...\n")
        if in_headers == None:
            headers = {'Authorization': 'Bearer ' + get_auth_key(),\
            'Content-Type': 'application/x-www-form-urlencoded'}
        else:
            headers = in_headers
        log.write_to_log ('url: ', in_url)
        if data != None:
            log.write_to_log('data: ', btos(data))
        else:
            log.write_to_log('data: None')
        log.write_to_log ('headers: ', headers)
        req = urllib.request.Request(in_url, data, headers)
        try:
            response = urllib.request.urlopen(req)
            log.write_to_log("RESPONSE URL: ", response.geturl())
            log.write_to_log("RESPONSE INFO:", response.info())
            log.write_to_log("RESPONSE CODE: ", response.getcode())
            response_data = btos(response.read())
            log.write_to_log('RESPONSE:\n', response_data, '\n')
            return response_data
        except (urllib.error.URLError):
            log.write_to_log("URLError:", sys.exc_info()[0])
            log.write_to_log("EXC INFO: ", sys.exc_info()[1])
            log.write_to_log("Fetch failed.")
            sys.exit()
            return None
        except:
            log.write_to_log("other error:", sys.exc_info()[0])
            log.write_to_log("Fetch failed.")
            sys.exit()
            return None

    # Get list of accounts
    # Returns: JSON from Oanda
    def get_accounts(self):
        return fetch(get_rest_url() + '/v1/accounts')

    # Get ID of account to trade with. Return it as a string.
    def get_account_id_primary(self):
        json_accounts = get_accounts()
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
        return fetch(get_rest_url() + '/v1/accounts/' + account_id)

    # Get list of open positions
    # Returns: JSON 
    def get_positions(self, account_id):
        return fetch( get_rest_url() + '/v1/accounts/' + account_id + '/positions')

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
        account_info = get_account(account_id)
        balance = json.loads(account_info)
        return balance['balance']

    # Fetch live prices for specified instruments that are available on the OANDA platform.
    # Returns: JSON
    # `instruments' argument must be URL encoded comma-separated, e.g. USD_JPY%2CEUR_USD
    def get_prices(self, instruments, since=None):
        url_args = '?instruments=' + instruments
        if since != None:
            url_args += '&since=' + since
        prices = fetch( get_rest_url() + '/v1/prices' + url_args )
        return prices

    # Get one ask price
    # Returns: Decimal
    def get_ask(self, instrument, since=None):
        prices_json = get_prices(instrument, since)
        prices_dict = json.loads(prices_json)
        for p in prices_dict['prices']:
            if p['instrument'] == instrument:
                return float(p['ask'])
        return None

    # Given an instrument (e.g. 'USD_JPY') and price, convert price to pips
    # Returns: decimal or None
    def to_pips(self, instrument, value):
        if instrument in pip_factors:
            return self.pip_factors[instrument] * value
        else:
            return None

    # Get spread, in pips, for given currency pairs (e.g. 'USD_JPY%2CEUR_USD')
    # Returns: dictionary of instruments and decimals
    def get_spreads(self, instruments, since=None ):
        log.write_to_log ('instruments: ', instruments)
        prices_json = self.get_prices(instruments, since)
        spreads = {}
        prices = json.loads(prices_json)
        for p in prices['prices']:
            spreads[p['instrument']] = to_pips( p['instrument'], (p['ask'] - p['bid']) )
        return spreads

    # Get one spread value
    def get_spread(self, instrument, since=None):
        spreads = get_spreads(instrument, since)
        if instrument in spreads:
            return spreads[instrument]
        else:
            return None

    # Buy an instrument
    # Returns: JSON
    def place_order(self, in_order):
        log.write_to_log ('Placing order...')
        post_args = {}
        post_args['instrument'] = in_order.instrument
        post_args['units'] = in_order.units
        post_args['side'] = in_order.side
        post_args['type'] = in_order.in_type
        post_args['expiry'] = in_order.expiry
        post_args['price'] = in_order.price
        if lowerBound != None:
            post_args['lowerBound'] = in_order.lowerBound
        if upperBound != None:
            post_args['upperBound'] = in_order.upperBound
        if stopLoss != None:
            post_args['stopLoss'] = in_order.stopLoss
        if takeProfit != None:
            post_args['takeProfit'] = in_order.takeProfit
        if trailingStop != None:
            post_args['trailingStop'] = in_order.trailingStop
        data = urllib.parse.urlencode(post_args)
        data = self.stob(data) # convert string to bytes
        return fetch( self.get_rest_url() + '/v1/accounts/' + self.get_account_id_primary() + '/orders', None, data)



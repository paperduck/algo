#!/usr/bin/python3
# Python 3.4

#--------------------------
import datetime
import sys
import urllib.request
import urllib.error
import time         # for sleep()
#from jq import jq
import json
#--------------------------
# Global constants
LOG_PATH = 'output.txt'
PRACTICE = True
PIP_FACTORS = {'AUD_CAD':10000, 'AUD_CHF':10000, 'AUD_HKD':10000, 'AUD_JPY':100, 'USD_JPY': 100}
#--------------------------
# clear log
def clear_log():
    with open(LOG_PATH, 'w') as f:
        f.write('')
        f.close()

# append to log
def write_to_log(*args):
    arg_list = list(args)
    msg = ""
    for a in arg_list:
        msg = msg + str(a)  
    with open(LOG_PATH, 'a') as f:
        f.write(msg)
        f.close()

# Get authorization key.
# Oanda was returning a '400 Bad Request' error 4 out of 5 times
#   until I removed the trailing '\n' from the string
#   returned by f.readline().
def get_auth_key():
    if PRACTICE:
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
def get_rest_url():
    if PRACTICE:
        return 'https://api-fxpractice.oanda.com'
    else:
        return 'https://api-fxtrade.oanda.com'
 
# Decode bytes to string using UTF8.
# Parameter `b' is assumed to have type of `bytes'.
def btos(b):
    return b.decode('utf_8')
#
def stob(s):
    return s.encode('utf_8')

# Helpful function for accessing Oanda's REST API
# Returns JSON as a string, or None.
# Prints error info to stdout.
def fetch(in_url, in_headers=None, data=None):
    write_to_log ("\nFetching...\n")
    if in_headers == None:
        headers = {'Authorization': 'Bearer ' + get_auth_key(), 'Content-Type': 'application/x-www-form-urlencoded'}
    else:
        headers = in_headers
    write_to_log ('url: ', in_url)
    if data != None:
        write_to_log('data: ', btos(data))
    else:
        write_to_log('data: None')
    write_to_log ('headers: ', headers)
    req = urllib.request.Request(in_url, data, headers)
    try:
        response = urllib.request.urlopen(req)
        write_to_log("RESPONSE URL: ", response.geturl())
        write_to_log("RESPONSE INFO:", response.info())
        write_to_log("RESPONSE CODE: ", response.getcode())
        response_data = btos(response.read())
        write_to_log('RESPONSE:\n', response_data, '\n')
        return response_data
    except (urllib.error.URLError):
        write_to_log("URLError:", sys.exc_info()[0])
        write_to_log("EXC INFO: ", sys.exc_info()[1])
        write_to_log("Fetch failed.")
        sys.exit()
        return None
    except:
        write_to_log("other error:", sys.exc_info()[0])
        write_to_log("Fetch failed.")
        sys.exit()
        return None

# Get list of accounts
# Returns: JSON from Oanda
def get_accounts():
    return fetch(get_rest_url() + '/v1/accounts')

# Get ID of account to trade with. Return it as a string.
def get_account_id_primary():
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
def get_account(account_id):
    return fetch(get_rest_url() + '/v1/accounts/' + account_id)

# Get list of open positions
# Returns: JSON 
def get_positions(account_id):
    return fetch( get_rest_url() + '/v1/accounts/' + account_id + '/positions')

# Get number of positions for a give account ID
# Returns: Number
def get_num_of_positions(account_id):
    positions = get_positions(account_id)
    position_list = json.loads(positions)
    num_pos = 0
    for p in position_list['positions']:
        num_pos = num_pos + 1
    return num_pos

# Get account balance for a given account ID
# Returns: Decimal number
def get_balance(account_id):
    account_info = get_account(account_id)
    balance = json.loads(account_info)
    return balance['balance']

# Fetch live prices for specified instruments that are available on the OANDA platform.
# Returns: JSON
# `instruments' argument must be URL encoded comma-separated, e.g. USD_JPY%2CEUR_USD
def get_prices(instruments, since=None):
    url_args = '?instruments=' + instruments
    if since != None:
        url_args += '&since=' + since
    prices = fetch( get_rest_url() + '/v1/prices' + url_args )
    return prices

# Get one ask price
# Returns: Decimal
def get_ask(instrument, since=None):
    prices_json = get_prices(instrument, since)
    prices_dict = json.loads(prices_json)
    for p in prices_dict['prices']:
        if p['instrument'] == instrument:
            return float(p['ask'])
    return None

# Given an instrument (e.g. 'USD_JPY') and price, convert price to pips
# Returns: decimal or None
def to_pips(instrument, value):
    if instrument in PIP_FACTORS:
        return PIP_FACTORS[instrument] * value
    else:
        return None

# Get spread, in pips, for given currency pairs (e.g. 'USD_JPY%2CEUR_USD')
# Returns: dictionary of instruments and decimals
def get_spreads( instruments, since=None ):
    write_to_log ('instruments: ', instruments)
    prices_json = get_prices(instruments, since)
    spreads = {}
    prices = json.loads(prices_json)
    for p in prices['prices']:
        spreads[p['instrument']] = to_pips( p['instrument'], (p['ask'] - p['bid']) )
    return spreads

# Get one spread value
def get_spread( instrument, since=None):
    spreads = get_spreads(instrument, since)
    if instrument in spreads:
        return spreads[instrument]
    else:
        return None

# Buy an instrument
# Returns: JSON
def place_order(instrument, units, side, in_type, expiry, price,\
lowerBound=None, upperBound=None, stopLoss=None, takeProfit=None,\
trailingStop=None):
    write_to_log ('Placing order...')
    post_args = {}
    post_args['instrument'] = instrument
    post_args['units'] = units
    post_args['side'] = side
    post_args['type'] = in_type
    post_args['expiry'] = expiry
    post_args['price'] = price
    if lowerBound != None:
        post_args['lowerBound'] = lowerBound
    if upperBound != None:
        post_args['upperBound'] = upperBound
    if stopLoss != None:
        post_args['stopLoss'] = stopLoss
    if takeProfit != None:
        post_args['takeProfit'] = takeProfit
    if trailingStop != None:
        post_args['trailingStop'] = trailingStop
    data = urllib.parse.urlencode(post_args)
    data = stob(data) # convert string to bytes
    return fetch( get_rest_url() + '/v1/accounts/' + get_account_id_primary() + '/orders', None, data)


if __name__ == "__main__":
    clear_log()
    write_to_log( datetime.datetime.now().strftime("%c") + "\n\n" )
    if PRACTICE:
        write_to_log('Using practice mode.')
    else:
        write_to_log('Using live account.')

    while True:
        num_of_positions = get_num_of_positions(get_account_id_primary())
        if num_of_positions == 0:
            # Enter a position
            spread = round(get_spread('USD_JPY'),2)
            if spread < 3:
                # buy
                cur_ask = round(get_ask('USD_JPY'),2)
                sl = cur_ask - 0.05
                tp = cur_ask + 0.10
                place_order('USD_JPY', 100, 'buy', 'market', None, None, None, None, sl, tp)
       # A little delay
        time.sleep(1)


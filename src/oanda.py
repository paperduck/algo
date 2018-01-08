# -*- coding: utf-8 -*-

"""
File            oanda.py
Python ver.     3.4
Description     Python module for Oanda fxTrade REST API.
                http://developer.oanda.com/
"""

#--------------------------
import datetime
import gzip
import json
import socket
import sys
import time
import traceback
import urllib.request
import urllib.error
import zlib
#--------------------------
from config import Config
from currency_pair_conversions import *
from instrument import Instrument
import util_date
from log import Log
from trade import *
from timer import Timer
import utils
import util_date
#--------------------------

class Oanda():
    """
    Class methods are used because only one instance of the Oanda
    class is ever needed.
    """
    account_id_primary = 0

    
    @classmethod
    def __str__(cls):
        return "oanda"


    @classmethod
    def get_auth_key(cls):
        """
        Get authorization key.
        Oanda was returning a '400 Bad Request' error 4 out of 5 times
        until I removed the trailing '\n' from the string
        returned by f.readline().
        """
        return Config.oanda_token
 

    """
    Return type: dict or none
    Sends a request to Oanda's REST API.
    """
    @classmethod
    def fetch(cls,
        in_url,
        in_headers={},
        in_data=None,
        in_origin_req_host=None,
        in_unverifiable=False,
        in_method=None):
        """
        Returns: dict or None.
        """
        Log.write('"oanda.py" fetch(): /*****************************\\' )
        Log.write('"oanda.py" fetch(): Parameters:\n\
            in_url: {0}\n\
            in_headers: {1}\n\
            in_data: {2}\n\
            origin_req_host: {3}\n\
            unverifiable: {4}\n\
            method: {5}\n\
            '.format(in_url, in_headers, utils.btos(in_data), in_origin_req_host,
            in_unverifiable, in_method))
        Log.write('"oanda.py" fetch(): \\*****************************/' )
        # If headers are specified, use those.
        if in_headers == {}:
            headers = {\
                'Authorization': 'Bearer ' + cls.get_auth_key(),\
                'Content-Type': 'application/x-www-form-urlencoded',\
                'Accept-Encoding': 'gzip, deflate'
            }
        else:
            headers = in_headers
        # send request
        req = urllib.request.Request(in_url, in_data, headers, in_origin_req_host, in_unverifiable, in_method)
        response = None
        # The Oanda REST API returns 404 error if you try to get trade info for a closed trade,
        #   so don't freak out if that happens.
        try:
            response = urllib.request.urlopen(req)
            # Check the response code.
            response_code = response.getcode()
            if response_code == 404:
                Log.write('"oanda.py" fetch(): Response code ', response_code)
            elif response_code == 415:
                # unsupported media type (content-encoding)
                Log.write('"oanda.py" fetch(): Response code 415: Unsupported media type')
            elif response_code == 204:
                # This happens when you request candlesticks from
                # a time at which there were none.
                Log.write('oanda.py fetch(): Response code was 204 (empty response).')
            elif response_code != 200:
                Log.write('"oanda.py" fetch(): Response code was {}.'.format(str(response_code)))
            # Other stuff
            #Log.write('"oanda.py" fetch(): RESPONSE URL:\n    ', response.geturl())
            #resp_info = response.info()
            # Get the response data.
            """
            response.info() is email.message_from_string(); it needs to be
            # cast to a string.
            """
            resp_data = None
            # See if the response data is encoded.
            header = response.getheader('Content-Encoding')
            if header != None:
                if header.strip().startswith('gzip'):
                    resp_data = utils.btos(gzip.decompress(response.read()))
                else:
                    if header.strip().startswith('deflate'):
                        resp_data = utils.btos( zlib.decompress( response.read() ) )
                    else:
                        resp_data = utils.btos( response.read() )
            else:
                resp_data = utils.btos(response.read())
            # Parse the JSON from Oanda into a dict, then return it.
            try:
                resp_data_dict = json.loads(resp_data)
                return resp_data_dict
            except:
                Log.write(
                    'oanda.py fetch(): Failed to parse the following JSON:\n\n{}\n\n'
                    .format(resp_data))
                return None
        except urllib.error.HTTPError as e:
            # 404
            Log.write('"oanda.py" fetch(): HTTPError:\n' + 
                'code: {}\nreason: {}\nheaders:\n{}\n'
                .format(e.code, e.reason, e.headers))
            return None
        except urllib.error.URLError:
            """
            sys.last_traceback
            https://docs.python.org/3.4/library/traceback.html
            """
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.write('"oanda.py" fetch(): URLError: ', exc_type)
            Log.write('"oanda.py" fetch(): EXC INFO: ', exc_value)
            Log.write('"oanda.py" fetch(): TRACEBACK:\n', traceback.print_exc(), '\n')
            Log.write('"oanda.py" fetch(): request:\n{}'.format(req))
            return None
        except OSError as e:
            Log.write('oanda.py fetch(): OSError w/message: {}'.format(e.strerror))
            return None
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.write('"oanda.py" fetch(): Exception: ', exc_type)
            Log.write('"oanda.py" fetch(): EXC INFO: ', exc_value)
            Log.write('"oanda.py" fetch(): TRACEBACK:\n', traceback.print_exc(), '\n')
            return None


    """
    Get list of accounts
    Returns: dict or None
    """
    @classmethod
    def get_accounts(cls):
        accounts = cls.fetch(Config.oanda_url + '/v1/accounts')
        if accounts != None:
            return accounts
        else:
            Log.write('oanda.py get_accounts(): Failed to get accounts.')
            return None

    
    """
    Get ID of account to trade with.
    Returns: String or None
    """
    @classmethod
    def get_account_id_primary(cls):
        if cls.account_id_primary == 0: # hasn't been cached yet
            accounts = cls.get_accounts()
            if accounts != None:
                for a in accounts['accounts']:
                    if a['accountName'] == 'Primary':
                        cls.account_id_primary = str(a['accountId'])
                        return cls.account_id_primary 
            else: 
                Log.write('oanda.py get_account_id_primary(): Failed to get accounts.')
                return None   
        else: # return cached value
            return cls.account_id_primary


    @classmethod
    def get_account_primary(cls):
        """
        Get info for primary account
        Returns: dict. Raises exception on error.
        """
        Log.write('"oanda.py" get_account(primary): Entering.')
        account = cls.fetch('{}/v1/accounts/{}'
            .format(Config.oanda_url, cls.get_account_id_primary())
            )
        if account == None:
            Log.write('"oanda.py" get_account(): Failed to get account.')
            return None
        else:
            return account


    @classmethod
    def get_account(cls, account_id):
        """
        Get account info for a given account ID
        Returns: dict or None 
        """
        Log.write('"oanda.py" get_account(): Entering.')
        account = cls.fetch(Config.oanda_url + '/v1/accounts/' + account_id)
        if account == None:
            Log.write('"oanda.py" get_account(): Failed to get account.')
            return None
        else:
            return account


    @classmethod
    def get_positions(cls, account_id):
        """
        Get list of open positions
        Returns: dict or None 
        """
        #Log.write('"oanda.py" get_positions(): Entering.')
        pos = cls.fetch(Config.oanda_url + '/v1/accounts/' + account_id + '/positions')
        if pos == None:
            Log.write('"oanda.py" get_positions(): Failed to get positions.')
            return None
        else:
            return pos


    @classmethod
    def get_num_of_positions(cls, account_id):
        """
        Get number of positions for a given account ID
        Returns: Integer
        """
        #Log.write('"oanda.py" get_num_of_positions(): Entering.')
        positions = cls.get_positions(account_id)
        if positions == None:
            Log.write('"oanda.py" get_num_of_positions(): Failed to get positions.')
            return None
        else:
            return len(positions['positions'])


    @classmethod
    def get_balance(cls, account_id):
        """
        Get account balance for a given account ID
        Returns: Decimal number
        """
        #Log.write('"oanda.py" get_balance(): Entering.')
        account = cls.get_account(account_id)
        if account == None:
            Log.write('"oanda.py" get_balance(): Failed to get account.')
            return None
        else:
            return account['balance']


    """
    Return type: dict or None
    Fetch live prices for specified instruments that are available on the OANDA platform.
    """
    @classmethod
    def get_prices(
        cls,
        instruments,    # [<Instrument>]
        since=None      # string
    ):
        url_args = '?instruments=' + utils.instruments_to_url(instruments)
        if since != None:
            url_args += '&since=' + since
        prices = cls.fetch(Config.oanda_url + '/v1/prices' + url_args )
        if prices == None:
            Log.write('"oanda.py" get_prices(): Failed to get prices.')
            return None
        else:
            return prices


    """
    Return type: Decimal or None
    Get one ask price
    TODO: check instrument string being passed in
    """
    @classmethod
    def get_ask(
        cls,
        instrument, # <Instrument> instance
        since=None  # string (see Oanda documentation)
    ):
        prices = cls.get_prices([instrument], since)
        if prices == None:
            Log.write('"oanda.py" get_ask(): Failed to get prices.')
            return None
        else:
            for p in prices['prices']:
                if p['instrument'] == instrument.get_name():
                    return float(p['ask'])


    """
    Return type: decimal or None
    """
    @classmethod
    def get_bid(cls,
        instrument, # <Instrument>
        since=None
    ):
        prices = cls.get_prices([instrument], since)
        if prices == None:
            Log.write('"oanda.py" get_bid(): Failed to get prices.')
            return None
        else:
            for p in prices['prices']:
                if p['instrument'] == instrument.get_name():
                    return float(p['bid'])


    """
    Return type: Dict or None
    """
    @classmethod
    def get_spread(cls, instrument, since=None):
        prices = cls.get_prices([instrument], since)
        if len(prices['prices']) != 1:
            return None
        p = prices['prices'][0]
        # Since Oanda doesn't always include status, add it manually.
        if 'status' not in p:
            p['status'] = ''
        spread =    {
                    "instrument": p['instrument'],
                    "time":p['time'],
                    "spread":price_to_pips(p['instrument'], (p['ask'] - p['bid'])),
                    "status":p['status']
                    }
        return spread


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
    @classmethod
    def get_spreads(
        cls,
        instruments, # [<Instrument>]
        since=None
    ):
        prices = cls.get_prices(instruments, since)
        if prices == None:
            Log.write('"oanda.py" get_spreads(): Failed to get prices.')
            return None
        else:
            spreads = []
            for p in prices['prices']:
                # Since Oanda doesn't always include status, add it manually.
                if 'status' not in p:
                    p['status'] = ''
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


    """
    Return type: dict or none
    Returns: information about the order (and related trade)
    Description: Place an order.

    If I place a trade that reduces another trade to closing, then I get a
    200 Code and information about the trade that closed. I.e. I don't get
    info about an opened trade.
    
    Oanda returns stuff like this:
    - instrument name
    - time
    - price // trigger price of order
    - tradeOpened
    - id
    - units
    - side
    - takeProfit
    - stopLoss
    - trailingStop
    - tradeClosed
    - tradeReduced
    """
    @classmethod
    def place_order(cls, in_order):
        Log.write ('"oanda.py" place_order(): Placing order...')
        request_args = {}
        if in_order.instrument != None:
            request_args['instrument'] = in_order.instrument.get_name()
        if in_order.units != None:
            request_args['units'] = in_order.units
        if in_order.go_long != None:
            # Oanda uses side={'buy' | 'sell'}
            if in_order.go_long:
                request_args['side'] = 'buy' 
            else:
                request_args['side'] = 'sell'
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
        data = utils.stob(urllib.parse.urlencode(request_args))
        result = cls.fetch(
            in_url="{}/v1/accounts/{}/orders".format(
                Config.oanda_url,
                cls.get_account_id_primary()
            ),
            in_data=data,
            in_method='POST'
            )
        if result == None:
            DB.bug('"oanda.py" place_order(): Failed to place order (1st try).')
            Log.write('"oanda.py" place_order(): Failed to place order; one more try.')
            time.sleep(1)
            result = cls.fetch(
                in_url="{}/v1/accounts/{}/orders".format(
                    Config.oanda_url,
                    cls.get_account_id_primary()
                ),
                in_data=data,
                in_method='POST'
                )
        if result == None:
            DB.bug('"oanda.py" place_order(): Failed to place order (2nd try).')
            Log.write('"oanda.py" place_order(): Failed to place order. Shutting down.')
            return None
        else:
            Log.write ('"oanda.py" place_order(): Order successfully placed.')
            return result


    """
    # Returns: Boolean
    # Is the market open?
    """
    @classmethod
    def is_market_open(
        cls,
        instrument  # <Instrument> instance
    ):
        prices = cls.get_prices([instrument])
        # 'status' only appears if instrument is halted
        try:
            if prices['prices'][0]['status'] == 'halted':
                return False
        except Exception:
            pass
        return True


    """
    Standard retail trading hours (no special access),
     or depending on broker.
    """
    market_opens = { 
        util_date.SUNDAY: [datetime.timedelta(hours=22)]
    }
    market_closes = {
        # 10pm UTC, 7am JST
        util_date.FRIDAY: [datetime.timedelta(hours=22)]
    }


    """
    Return type: datetime.timedelta
    Return value:
        timedelta of 0 if market is already closed,
        otherwise timedelta until market closes
    """
    @classmethod
    def get_time_until_close(cls):
        zero = datetime.timedelta()
        if not cls.is_market_open(Instrument(4)): # actually check the broker first
            return zero
        now = datetime.datetime.utcnow()
        now_day = now.isoweekday()
        now_delta = datetime.timedelta(
            hours=now.hour,
            minutes=now.minute,
            seconds=now.second,
            microseconds=now.microsecond
        )
        now_to_soonest_close = datetime.timedelta(days=8) # > 1 week
        total_delta_to_close = zero
        day_index = now_day
        # Starting from today, iterate through each weekday and 
        # see if the market will close that day.
        for i in range(1, 8): # match python datetime.isoweekday()
            closes = cls.market_closes.get(day_index)
            if closes != None:
                # there is at least one close this day
                for c in closes:
                    if now_delta < c and c - now_delta < now_to_soonest_close:
                        # new soonest close
                        now_to_soonest_close = c - now_delta
                # If there is an open time today:
                #   If there was a close, look for open < soonest close.
                #   Else, market is closed
                opens = cls.market_opens.get(day_index)
                if opens != None:
                    if now_to_soonest_close < datetime.timedelta(days=8):
                        for o in opens:
                            if now_delta < o and (o - now_delta) < now_to_soonest_close:
                                # market will open before closing
                                return zero
                    else:
                        # market is closed
                        return zero
                # return soonest close
                total_delta_to_close += now_to_soonest_close
                return total_delta_to_close
            # cycle the index 
            total_delta_to_close += datetime.timedelta(hours=24)
            day_index += 1
            if day_index > 7:
                day_index = 1
        Log.write('oanda.py get_time_until_close(): Close time not found.')
        raise Exception


    """
    Return type: datetime.timedelta
    Return value: Time passed since last market close, regardless of 
        current open/close status.
    """
    @classmethod
    def get_time_since_close(cls):
        # Iterate backwards through days and return the most recent time.
        now = datetime.datetime.utcnow()
        day_iter = now.isoweekday()
        now_delta = datetime.timedelta(
            hours=now.hour,
            minutes=now.minute,
            seconds=now.second,
            microseconds=now.microsecond
        )
        zero = datetime.timedelta()
        latest_close_to_now_delta = datetime.timedelta(days=8) # > 1 week
        total_delta_since_close = zero
        for d in range(1,8):
            closes = cls.market_closes.get(day_iter)
            if closes != None:
                # find most recent close this day
                for c in closes:
                    if now_delta - c < latest_close_to_now_delta:
                        latest_close_to_now_delta = now_delta - c
                total_delta_since_close += latest_close_to_now_delta
                return total_delta_since_close
            # move to previous day
            day_iter -= 1
            if day_iter < 1:
                day_iter = 7
            total_delta_since_close += datetime.timedelta(hours=24)
        raise Exception
        

    """
    Get transaction history
    Returns: dict or None
    """
    @classmethod
    def get_transaction_history(cls, maxId=None, minId=None, count=None, instrument=None, ids=None):
        #Log.write('"oanda.py" get_transaction_history(): Entering.')

        args = ''
        if maxId != None:
            if args != '':
                args = args + '&'
            args = args + 'maxId=' + str(maxId)
        if minId != None:
            if args != '':
                args = args + '&'
            args = args + 'minId=' + str(minId)
        if count != None:
            if args != '':
                args = args + '&'
            args = args + 'count=' + str(count)
        if instrument != None:
            if args != '':
                args = args + '&'
            args = args + 'instrument=' + instrument.get_name()
        if ids != None:
            if args != '':
                args = args + '&'
            args = args + 'ids=' & str(ids)
        trans = cls.fetch(
             in_url='{}/v1/accounts/{}/transactions?{}'
            .format(Config.oanda_url, cls.get_account_id_primary(), args)
            )
        if trans == None:
            DB.bug('"oanda.py" get_transaction_history(): Failed to fetch transaction history.')
            Log.write('"oanda.py" get_transaction_history(): Failed to fetch transaction history.')
            return None
        else:
            return trans


    """
    Return type: dict or None
    """
    @classmethod
    def get_instrument_history(
        cls,
        in_instrument,          # <Instrument>
        granularity=None,       # string
        count=None,             # optional- int - leave out if both start & end specified
        start=None,             # optional- datetime
        end=None,               # optional- datetime
        candle_format=None,     # optional - string - Oanda defaults to
                                # bid/ask (versus midpoint)
        include_first=None,     # optional - bool - Oanda wants 'true'/'false'
        daily_alignment=None,   # 0 to 23 - optional
        alignment_timezone=None,# timezone - optional
        weekly_alignment=None   # 'Monday' etc. - optional
    ):
        if count != None and start != None and end != None:
            raise Exception
        args='instrument=' + in_instrument.get_name()
        if granularity != None:
            args = args + '&granularity=' + granularity
        if count != None:
            args = args + '&count=' + str(count)
        if start != None:
            args = args + '&start=' + utils.url_encode(util_date.date_to_string(start))
        if end != None:
            args = args + '&end=' + utils.url_encode(util_date.date_to_string(end))
        if candle_format != None:
            args = args + '&candleFormat=' + candle_format
        if include_first != None:
            if include_first:
                args = args + '&includeFirst=' + 'true'
            else:
                args = args + '&includeFirst=' + 'true'
        if daily_alignment != None:
            args = args + '&dailyAlignment=' + str(daily_alignment)
        if alignment_timezone != None:
            args = args + '&alignmentTimezone=' + alignment_timezone
        if weekly_alignment != None:
            args = args + '&weeklyAlignment=' + weekly_alignment

        result = cls.fetch(
            in_url='{}/v1/candles?{}'.format(Config.oanda_url, args)
        )
        if result == None:
            DB.bug('"oanda.py" get_instrument_history(): Failed to fetch.')
            Log.write('"oanda.py" get_instrument_history(): Failed to fetch.')
            return None
        else:
            return result


    """
    Returns:    Tuple: (
                    True=trade closed; False=not closed
                    Reason trade closed (or None)
                )
    TODO: Function name implies bool, but return val is tuple.
    Go through all transactions that have occurred since a given order, and see if any of those
    transactions have closed or canceled the order.
    """
    @classmethod
    def is_trade_closed(cls, trade_id):
        Log.write('"oanda.py" is_trade_closed(): Entering with trade ID {}'
            .format(trade_id))
        start = Timer.start()
        num_attempts = 2
        while num_attempts > 0:
            Log.write('"oanda.py" is_trade_closed(): Remaining attempts: ', str(num_attempts))
            transactions = cls.get_transaction_history(minId=trade_id)
            if transactions == None:
                Log.write('"oanda.py" is_trade_closed(): Failed to get transaction history.')
                return None
            else:
                for trans in transactions['transactions']:
                    Log.write('"oanda.py" is_trade_closed(): Searching transactions for trade_id ({}):\n{}'
                        .format(trade_id, trans))
                    # TODO: Check other cases as well so I can return False quickly.
                    if trans['type'] == 'MARKET_ORDER_CREATE':
                        if 'tradeReduced' in trans:
                            if str(trans['tradeReduced']['id']) == str(trade_id):
                                Log.write('"oanda.py" is_trade_closed(): MARKET_ORDER_CREATE')
                                Timer.stop(start, 'Oanda.is_trade_closed()', 'market order create')
                                return (True, TradeClosedReason.reduced)
                        # trans['tradeOpened'] will be the original trade
                    if trans['type'] == 'TRADE_CLOSE':
                        if str(trans['tradeId']) == str(trade_id):
                            Log.write('"oanda.py" is_trade_closed(): TRADE_CLOSE')
                            Timer.stop(start, 'Oanda.is_trade_closed()', 'trade close')
                            return (True, TradeClosedReason.manual)
                    if trans['type'] == 'MIGRATE_TRADE_CLOSE':
                        if str(trans['tradeId']) == str(trade_id):
                            Log.write('"oanda.py" is_trade_closed(): MIGRATE_TRADE_CLOSED')
                            Timer.stop(start, 'Oanda.is_trade_closed()', 'migrate trade closed')
                            return (True, TradeClosedReason.migrated)
                    if trans['type'] == 'STOP_LOSS_FILLED':
                        Log.write(str(trans['tradeId']), ' ?= ', str(trade_id))
                        if str(trans['tradeId']) == str(trade_id):
                            Log.write('match')
                            Log.write('"oanda.py" is_trade_closed(): STOP_LOSS_FILLED')
                            Timer.stop(start, 'Oanda.is_trade_closed()', 'stop loss filled')
                            return (True, TradeClosedReason.sl)
                    if trans['type'] == 'TAKE_PROFIT_FILLED':
                        if str(trans['tradeId']) == str(trade_id):
                            Log.write('"oanda.py" is_trade_closed(): TAKE_PROFIT_FILLED')
                            Timer.stop(start, 'Oanda.is_trade_closed()', 'take profit filled')
                            return (True, TradeClosedReason.tp)
                    if trans['type'] == 'TRAILING_STOP_FILLED':
                        if str(trans['tradeId']) == str(trade_id):
                            Log.write('"oanda.py" is_trade_closed(): TRAILING_STOP_FILLED')
                            Timer.stop(start, 'Oanda.is_trade_closed()', 'trailing stop filed')
                            return (True, TradeClosedReason.ts)
                    if trans['type'] == 'MARGIN_CLOSEOUT':
                        if str(trans['tradeId']) == str(trade_id):
                            Log.write('"oanda.py" is_trade_closed(): MARGIN_CLOSEOUT')
                            Timer.stop(start, 'Oanda.is_trade_closed()', 'margin closeout')
                            return (True, TradeClosedReason.margin_closeout)
            num_attempts = num_attempts - 1
            # Delay to allow the trade to be processed on the dealer end
            time.sleep(1)
        Log.write('"oanda.py" is_trade_closed(): Unable to locate trade.')
        Timer.stop(start, 'Oanda.is_trade_closed()', 'unable to locate')
        return (False, None)


    """
    Return type: Instance of <Trades> or None
    Get info about all open trades
    """
    @classmethod
    def get_trades(cls):
        #Log.write('"oanda.py" get_trades(): Entering.')
        trades_oanda = cls.fetch('{}/v1/accounts/{}/trades/'
            .format(Config.oanda_url,str(cls.get_account_id_primary()))
            )
        if trades_oanda == None:
            Log.write('"oanda.py" get_trades(): Failed to get trades from Oanda.')
            return None
        else:
            ts = Trades()
            for t in trades_oanda['trades']: 
                # format into a <Trade>
                go_long = None
                if t['side'] == 'buy':
                    going_long = True
                else:
                    going_long = False
                ts.append(Trade(
                    broker_name = cls.__str__(),
                    instrument = Instrument(Instrument.get_id_from_name(t['instrument'])),
                    go_long = going_long,
                    stop_loss = t['stopLoss'],
                    strategy = None,
                    take_profit = t['takeProfit'],
                    trade_id = t['id']
                ))
            return ts


    @classmethod
    def get_trade(cls, trade_id):
        """
        Get info about a particular trade.
        """
        Log.write('"oanda.py" get_trade(): Entering.')
        t = cls.fetch(
            '{}/v1/accounts/{}/trades/{}'.format(
                Config.oanda_url,
                str(cls.get_account_id_primary()),
                str(trade_id)
            )
        )
        if t != None:
            go_long = None
            if t['side'] == 'buy':
                going_long = True
            else:
                going_long = False
            return Trade(
                    broker_name = cls.__str__(),
                    instrument = Instrument(Instrument.get_id_from_name(t['instrument'])),
                    go_long = going_long,
                    stop_loss = t['stopLoss'],
                    strategy = None,
                    take_profit = t['takeProfit'],
                    trade_id = t['id']
                )
        else:
            # Apparently the Oanda REST API returns a 404 error if the trade has closed, so don't freak out here.
            Log.write('"oanda.py" get_trade(): Failed to get trade info for trade with ID ', trade_id, '.')
            return None


    """
    Returns: dict or None
    Get order info
    """
    @classmethod
    def get_order_info(cls, order_id):
        response = cls.fetch(\
             Config.oanda_url + '/v1/accounts/' + str(cls.get_account_id_primary()) + '/orders/' + str(order_id) )
        if response == None:
            Log.write('"oanda.py" get_order_info(): Failed to get order info.')
            return None
        else:
            return response
        
    """
    # Returns: dict or None
    # Modify an existing order
    """
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
        data = utils.stob(data) # convert string to bytes

        response = cls.fetch(
            in_url= + '{}/v1/accounts/{}/orders/{}'
            .format(
                Config.oanda_url,
                str(cls.get_account_id_primary()),
                str(in_order_id)
            ),
            in_data=data,
            in_method='PATCH'
        )
        if response == None:
            Log.write('"oanda.py" modify_order(): Failed to modify order.')
            return None
        else:
            return response


    """
    Modify an existing trade
    Returns: dict or None
    """
    @classmethod
    def modify_trade(cls, trade_id, stop_loss=0, take_profit=0, trailing_stop=0):
        #Log.write('"oanda.py" modify_trade(): Entering.')
        request_args = {}
        if stop_loss != 0:
            request_args['stopLoss'] = stop_loss
        if take_profit != 0:
            request_args['takeProfit'] = take_profit
        if trailing_stop != 0:
            request_args['trailingStop'] = trailing_stop
        data = urllib.parse.urlencode(request_args)
        data = utils.stob(data) # convert string to bytes
    
        response = cls.fetch(
            in_url='{}/v1/accounts/{}/trades/{}'
            .format(
                Config.oanda_url,
                str(cls.get_account_id_primary()),
                str(trade_id)
            ),
            in_data=data,
            in_method='PATCH'
        )
        if response != None:
            return response
        else:
            Log.write('"oanda.py" modify_trade(): Failed to modify trade.')
            return None



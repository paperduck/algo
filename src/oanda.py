"""
Custom Python wrapper for Oanda's REST-V20 API.
This wrapper might be incomplete.
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
        """Return type: string
           Return value: authentication token
        Oanda was returning a '400 Bad Request' error 4 out of 5 times
        until I removed the trailing '\n' from the string
        returned by f.readline().
        """
        return Config.oanda_token
 

    @classmethod
    def fetch(cls,
        in_url,
        in_headers={},
        in_data=None,
        in_origin_req_host=None,
        in_unverifiable=False,
        in_method=None):
        """Return type: dict or none
        Sends a request to Oanda's REST API.
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
                'Content-Type': 'application/json',\
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Datetime-Format': 'RFC3339'
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


    @classmethod
    def get_accounts(cls):
        """Returns: dict or None
        Get list of accounts
        """
        accounts = cls.fetch(Config.oanda_url + '/v3/accounts')
        if accounts != None:
            return accounts
        else:
            Log.write('oanda.py get_accounts(): Failed to get accounts.')
            return None

    
    '''@classmethod
    def get_account_id_primary(cls):
        """Get ID of account to trade with.
        Returns: String or None
        """
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
    '''


    '''@classmethod
    def get_account_primary(cls):
        """
        Get info for primary account
        Returns: dict. Raises exception on error.
        """
        Log.write('"oanda.py" get_account(primary): Entering.')
        account = cls.fetch('{}/v3/accounts/{}'
            .format(Config.oanda_url, cls.get_account_id_primary())
            )
        if account == None:
            Log.write('"oanda.py" get_account(): Failed to get account.')
            return None
        else:
            return account
    '''


    @classmethod
    def get_account(cls, account_id):
        """Returns: dict or None 
        Get account info for a given account ID
        """
        Log.write('"oanda.py" get_account(): Entering.')
        account = cls.fetch(Config.oanda_url + '/v3/accounts/' + account_id)
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
        pos = cls.fetch(Config.oanda_url + '/v3/accounts/' + account_id + '/positions')
        if pos == None:
            Log.write('"oanda.py" get_positions(): Failed to get positions.')
            return None
        else:
            return pos


    @classmethod
    def get_num_of_positions(cls, account_id):
        """Returns: Integer
        Get number of positions for a given account ID
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
        """Returns: Decimal number
        Get account balance for a given account ID
        """
        #Log.write('"oanda.py" get_balance(): Entering.')
        account = cls.get_account(account_id)
        if account == None:
            Log.write('"oanda.py" get_balance(): Failed to get account.')
            return None
        else:
            return account['balance']


    @classmethod
    def get_prices(
        cls,
        instruments,    # [<Instrument>]
        since=None      # string
    ):
        """Return type: dict or None
        Fetch live prices for specified instruments that are available on the OANDA platform.
        """
        url_args = 'instruments=' + utils.instruments_to_url(instruments)
        if since != None:
            url_args += '&since=' + since
        prices = cls.fetch( '{}/v3/accounts/{}/pricing?{}'
            .format(Config.oanda_url, Config.account_id, url_args) )
        if prices == None:
            Log.write('"oanda.py" get_prices(): Failed to get prices.')
            return None
        else:
            return prices


    @classmethod
    def get_ask(
        cls,
        instrument, # <Instrument> instance
        since=None  # string (see Oanda documentation)
    ):
        """Return type: Decimal or None
        Get lowest ask price.
        """
        prices = cls.get_prices([instrument], since)
        if prices == None:
            Log.write('"oanda.py" get_ask(): Failed to get prices.')
            return None
        else:
            try:
                for p in prices['prices']:
                    if p['instrument'] == instrument.get_name():
                        return float(p['asks'][0]['price']) 
            except Excpetion:
                Log.write('oanda.py get_ask(): Failed to extract ask from price data. Price data:\n{}'
                    .format(prices))
                raise Exception


    @classmethod
    def get_bid(cls,
        instrument, # <Instrument>
        since=None
    ):
        """Return type: decimal or None
        Get highest bid price.
        """
        prices = cls.get_prices([instrument], since)
        if prices == None:
            Log.write('"oanda.py" get_bid(): Failed to get prices.')
            return None
        else:
            try:
                for p in prices['prices']:
                    if p['instrument'] == instrument.get_name():
                        return float(p['bids'][0]['price'])
            except Exception:
                Log.write('oanda.py get_bid(): Failed to extract bid from price data. Price data:\n{}'
                    .format(prices))
                raise Exception


    @classmethod
    def get_spread(cls, instrument, since=None):
        """Return type: Dict of spread data or None
        """
        prices = cls.get_prices([instrument], since)
        if len(prices['prices']) != 1:
            return None
        p = prices['prices'][0]
        spread =    {
                    "instrument": p['instrument'],
                    "time":p['time'],
                    "spread":price_to_pips(p['instrument'], (float(p['asks'][0]['price']) - float(p['bids'][0]['price']))),
                    "status":p['status']
                    }
        return spread


    @classmethod
    def get_spreads(
        cls,
        instruments, # [<Instrument>]
        since=None
    ):
        """Returns: list
        Get spread, in pips, for given currency pairs (e.g. 'USD_JPY%2CEUR_USD')
        """
        prices = cls.get_prices(instruments, since)
        if prices == None:
            Log.write('"oanda.py" get_spreads(): Failed to get prices.')
            return None
        else:
            spreads = []
            for p in prices['prices']:
                spreads.append(
                    {
                        "instrument":p['instrument'],
                        "time":p['time'],
                        "spread":price_to_pips(p['instrument'], (float(p['asks'][0]['price']) - float(p['bids'][0]['price']))),
                        "status":p['status']
                    }
                )
            Log.write('"oanda.py" get_spreads(): Spreads:\n{}\n'
                .format(spreads))
            return spreads


    @classmethod
    def place_order(cls, in_order):
        """Return type: dict or none
        Return value: information about the order (and related trade)
        Description: Place an order.

        If I place a trade that reduces another trade to closing, then I get a
        200 Code and information about the trade that closed. I.e. I don't get
        info about an opened trade.
        """
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
            in_url="{}/v3/accounts/{}/orders".format(
                Config.oanda_url,
                Config.account_id
            ),
            in_data=data,
            in_method='POST'
            )
        if result == None:
            DB.bug('"oanda.py" place_order(): Failed to place order (1st try).')
            Log.write('"oanda.py" place_order(): Failed to place order; one more try.')
            time.sleep(1)
            result = cls.fetch(
                in_url="{}/v3/accounts/{}/orders".format(
                    Config.oanda_url,
                    Config.account_id
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


    @classmethod
    def is_market_open(
        cls,
        instrument  # <Instrument> instance
    ):
        """Return type: boolean
        Return value: true if market currently open, according to Oanda's API.
        """
        prices = cls.get_prices([instrument])
        try:
            return prices['prices'][0]['status'] == 'tradeable'
        except Exception:
            Log.write(
                'oanda.py is_market_open(): Failed to get key \'status\'. \ninstr:{}\nprices: {}'.format(instrument, prices))
            raise Exception


    """
    Standard retail trading hours (no special access),
     or depending on broker.
    """
    market_opens = { 
        # 10pm UTC, 7am JST
        util_date.SUNDAY: [datetime.timedelta(hours=22)]
    }
    market_closes = {
        # 10pm UTC, 7am JST
        util_date.FRIDAY: [datetime.timedelta(hours=22)]
    }


    @classmethod
    def get_time_until_close(cls):
        """Return type: datetime.timedelta
        Return value:
            timedelta of 0 if market is already closed,
            otherwise timedelta until market closes
        """
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


    @classmethod
    def get_time_since_close(cls):
        """Return type: datetime.timedelta
        Return value: Time passed since last market close, regardless of 
            current open/close status.
        """
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
        

    @classmethod
    def get_transactions_since_id(cls, start_id):
        """Returns: dict or None
        Gets transactions since start_id
        """
        transactions = cls.fetch(
             in_url='{}/v3/accounts/{}/transactions/sinceid?id={}'
            .format(Config.oanda_url, Config.account_id, start_id)
            )
        if transactions == None:
            DB.bug('"oanda.py" get_transaction_since_id(): Failed to fetch transaction history.')
            Log.write('"oanda.py" get_transaction_since_id(): Failed to fetch transaction history.')
            return None
        else:
            return transactions
        

    '''
    @classmethod
    def get_transaction_history(cls, maxId=None, minId=None, count=None, instrument=None, ids=None):
        """Returns: dict or None
        Get transaction history
        """
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
            .format(Config.oanda_url, Config.account_id, args)
            )
        if trans == None:
            DB.bug('"oanda.py" get_transaction_history(): Failed to fetch transaction history.')
            Log.write('"oanda.py" get_transaction_history(): Failed to fetch transaction history.')
            return None
        else:
            return trans
    '''


    @classmethod
    def get_instrument_history(
        cls,
        in_instrument,      # <Instrument>
        granularity,        # string
        count,              # optional- int - leave out if both start & end specified
        from_time,          # optional- datetime
        to,                 # optional- datetime
        price,              # optional - string
        include_first,      # optional - bool - Oanda wants 'true'/'false'
        daily_alignment,    # 0 to 23 - optional
        alignment_timezone, # timezone - optional
        weekly_alignment    # 'Monday' etc. - optional
    ):
        """Return type: dict or None
        """
        if count != None and from_time != None and to != None:
            raise Exception
        args=''
        if granularity != None:
            args = args + '&granularity=' + granularity
        if count != None:
            args = args + '&count=' + str(count)
        if from_time != None:
            args = args + '&from=' + utils.url_encode(util_date.date_to_string(from_time))
        if to != None:
            args = args + '&to=' + utils.url_encode(util_date.date_to_string(to))
        if price != None:
            args = args + '&price=' + price
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
            in_url='{}/v3/instruments/{}/candles?{}'.format(Config.oanda_url, in_instrument.get_name(), args)
        )
        if result == None:
            DB.bug('"oanda.py" get_instrument_history(): Failed to fetch.')
            Log.write('"oanda.py" get_instrument_history(): Failed to fetch.')
            return None
        else:
            return result


    @classmethod
    def is_trade_closed(cls, trade_id):
        """Returns:
            Tuple: (
                True=trade closed; False=not closed
                <TradeClosedReason> or None
            )
        TODO: Function name implies bool, but return val is tuple.
        Go through all transactions that have occurred since a given order, and see if any of those
        transactions have closed or canceled the order.
        """
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


    @classmethod
    def get_open_trades(cls):
        """Return type: Instance of <Trades> or None
        Get info about all open trades
        """
        #Log.write('"oanda.py" get_open_trades(): Entering.')
        trades_oanda = cls.fetch('{}/v3/accounts/{}/openTrades/'
            .format(Config.oanda_url,str(Config.account_id))
            )
        if trades_oanda == None:
            Log.write('"oanda.py" get_open_trades(): Failed to get trades from Oanda.')
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
        """Returns: <Trade> or None
        Get info about a particular trade.
        """
        Log.write('"oanda.py" get_trade(): Entering.')
        trades = cls.fetch(
            '{}/v3/accounts/{}/trades/{}'.format(
                Config.oanda_url,
                str(Config.account_id),
                str(trade_id)
            )
        )
        if trades != None:
            go_long = None
            if trades['side'] == 'buy':
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


    @classmethod
    def get_order_info(cls, order_id):
        """Returns: dict or None
        Get order info
        """
        response = cls.fetch(\
             Config.oanda_url + '/v3/accounts/' + str(Config.account_id) + '/orders/' + str(order_id) )
        if response == None:
            Log.write('"oanda.py" get_order_info(): Failed to get order info.')
            return None
        else:
            return response
        

    @classmethod
    def modify_trade(
        cls,
        trade_id,
        take_profit_price=None,
        #take_profit_time_in_force=None,
        #take_profit_good_til_date=None,
        #take_profit_clientExtensions=None,
        stop_price=None,
        trailing_stop_distance=None
    ):
        """Returns:
        This is trimmed down from Oanda's v20 API.
        """
        #Log.write('"oanda.py" modify_trade(): Entering.')

        request_body = {}
        if take_profit_price:
            request_body['takeProfit'] = {}
            request_body['takeProfit']['price'] = take_profit_price
        if stop_price:
            request_body['stopLoss'] = {}
            request_body['stopLoss']['price'] = stop_price
        if trailing_stop_distance:
            request_body['trailingStopLoss'] = {}
            request_body['trailingStopLoss']['distance'] = trailing_stop_distance

        response = cls.fetch(
            in_url='{}/v3/accounts/{}/trades/{}/orders'
            .format(
                Config.oanda_url,
                Config.account_id,
                str(trade_id)
            ),
            in_data=request_body,
            in_method='PUT'
        )
        if response != None:
            return response
        else:
            Log.write('"oanda.py" modify_trade(): Failed to modify trade.')
            return None



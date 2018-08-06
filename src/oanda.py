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
    Class methods are used because only one instance is ever needed and unlike
    static methods, the methods need to share data.
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
        in_url, # string
        in_headers={}, # dict
        in_data=b"", # typically JSON string, encoded to bytes
        in_origin_req_host=None, # string
        in_unverifiable=False, # bool
        in_method='GET' # string
    ):
        """Return type: dict on success, None on failure.
        Sends a request to Oanda's API.
        """
        # If headers are specified, use those.
        headers = None
        if in_headers == {}:
            headers = {\
                'Authorization': 'Bearer ' + cls.get_auth_key(),\
                'Content-Type': 'application/json',\
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Datetime-Format': 'RFC3339',
                'Content-Length': len(in_data)
            }
        else:
            headers = in_headers
        Log.write('"oanda.py" fetch(): /*****************************\\' )
        Log.write('"oanda.py" fetch():\n\
            {}:{}\n\
            in_data: {}     origin_req_host: {}     unverifiable: {}\n\
            headers: {}\
            '.format(
                in_url, utils.btos(in_data), in_origin_req_host,
                in_unverifiable, in_method, headers)
            )
        Log.write('"oanda.py" fetch(): \\*****************************/' )
        # send request
        req = urllib.request.Request(in_url, in_data, headers, in_origin_req_host, in_unverifiable, in_method)
        response = cls.send_http_request(req)
        while not response[0] and response[2]:
            # Failure. Wait and try again.  
            time.sleep(1)
            Log.write('oanda.py fetch(): Resending request...')
            response = cls.send_http_request(req)
        if response[0]:
            # Success. Get the response data.
            """ "response.info() is email.message_from_string(); it needs to be
            cast to a string."
            """
            return response[1]
        else:
            # Gave up trying.
            return None


    @classmethod
    def read_response(cls, response):
        """Returns: response data as dict
        This is a helper function for fetch().
        """
        header = response.getheader('Content-Encoding')
        if header != None:
            # Check how the response data is encoded.
            if header.strip().startswith('gzip'):
                Log.write('oanda.py read_response(): gzip payload')
                return utils.btos(gzip.decompress(response.read()))
            else:
                if header.strip().startswith('deflate'):
                    Log.write('oanda.py read_response(): zlib payload')
                    return utils.btos( zlib.decompress( response.read() ) )
                else:
                    Log.write('oanda.py read_response(): Unknown header.')
                    return utils.btos( response.read() )
        else:
            Log.write('oanda.py read_response(): No header.')
            return utils.btos(response.read())
        

    @classmethod
    def send_http_request(
        cls,
        request, # request object
    ):
        """Returns tuple:
        (
            bool:   was success
            object: success     -> data(probably dict)
                    not success -> error_object
            bool:   should retry
        )
        This is a helper function for fetch().
        """
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            # e.code():
            # 204: No candlesticks during requested time.
            # 400: 
            # 404: Tried to get trade info for a closed trade.
            # 415: unsupported media type (content-encoding)
            # 503: Service Unavailable (e.g. scheduled maintenance)
            Log.write('oanda.py send_http_request(): HTTPError:\n{}'.format(str(e)))
            if e.code in ['503']:
                return (False, e, True)
            else:
                return (False, e, False)
        except urllib.error.URLError as e:
            # https://docs.python.org/3.4/library/traceback.html
            Log.write('oanda.py send_http_request(): URLError:\n{}'.format(str(e)))
            return (False, e, False)
        except ConnectionError as e:
            Log.write('oanda.py send_http_request(): ConnectionError:\n{}'.format(str(e)))
            return (False, e, True)
        except OSError as e:
            # Not sure why this happens. Usually when market is closed.
            Log.write('oanda.py send_http_request(): OSError:\n{}'.format(str(e)))
            return (False, e, True)
        except Exception as e:
            # some other error type
            Log.write('oanda.py send_http_request(): some other error:\n{}'.format(str(e)))
            """
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.write('oanda.py send_http_request(): Exception: ', exc_type)
            Log.write('oanda.py send_http_request(): EXC INFO: ', exc_value)
            Log.write('oanda.py send_http_request(): TRACEBACK:\n', traceback.print_exc(), '\n')
            """
            return (False, e, True)
        else:
            # no exceptions == success
            Log.write(
                'oanda.py fetch(): successful response.info(): {}'
                .format(response.info()) )
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
            try:
                return ( True, json.loads(resp_data) )
            except:
                Log.write(
                    'oanda.py send_http_request(): Failed to parse JSON:\n{}'
                    .format( resp_data ) )
                raise Exception


    @classmethod
    def get_accounts(cls):
        """Returns: dict
        Get list of accounts
        """
        return cls.fetch(Config.oanda_url + '/v3/accounts')


    @classmethod
    def get_account(cls, account_id):
        """Returns: dict or None 
        Get account info for a given account ID.
        """
        account = cls.fetch(Config.oanda_url + '/v3/accounts/' + account_id)
        if account == None:
            Log.write('"oanda.py" get_account(): Failed to get account.')
            return None
        else:
            return account


    @classmethod
    def get_account_summary(
        cls,
        account_id # string
    ):
        """return type: dict
        """
        return cls.fetch( 
            Config.oanda_url + '/v3/accounts/{}/summary'.format(account_id)
        )


    @classmethod
    def get_margin_available(cls, account_id):
        """Return type:  float
           Return value: margin available
        """
        account_summary = cls.get_account_summary(account_id)
        try:
            return float(account_summary['account']['marginAvailable'])
        except:
            Log.write('oanda.py get_margin_available(): Failed to extract marginAvailable.')
            raise Exception
            

    @classmethod
    def get_margin_rate(
        cls, 
        instrument # <Instrument> instance
    ):
        """Return type: float
        """
        query_args = '?instruments={}'.format(instrument.get_name())
        instruments_info = cls.fetch(
            in_url='{}/v3/accounts/{}/instruments{}'
                .format(Config.oanda_url, Config.account_id, query_args)
        )
        try:
            Log.write('oanda.py get_margin_rate(): returned data: \n{}'
                .format(instruments_info))
            return float( instruments_info['instruments'][0]['marginRate'] )
        except:
            Log.write('oanda.py get_margin_rate(): Failed to extract ' \
                + 'marginRate. Oanda returned:\n{}'
                .format(instruments_info)
            )
            raise Exception


    @classmethod
    def get_positions(cls, account_id):
        """
        Get list of open positions
        Returns: dict or None 
        """
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
        positions = cls.get_positions(account_id)
        if positions == None:
            Log.write('"oanda.py" get_num_of_positions(): Failed to get positions.')
            return None
        else:
            return len(positions['positions'])


    @classmethod
    def get_balance(cls, account_id):
        """Return type: Decimal number
        Get account balance for a given account ID
        """
        account_summary = cls.get_account_summary(account_id)
        try:
            return float(account_summary['account']['balance'])
        except:
            Log.write('oanda.py get_balance(): Failed to extract balance from account summary. Summary from broker was:\n{}'
            .format(account_summary))
            raise Exception
        

    @classmethod
    def get_prices(
        cls,
        instruments,    # [<Instrument>]
        since=None      # string
    ):
        """Return type: dict or None
        Fetch live prices for specified instruments that are available on the OANDA platform.
        """
        Log.write('oanda.py get_prices()')
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
        Log.write('oanda.py get_ask()')
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
        Log.write('oanda.py get_bid()')
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
    def get_spreads(
        cls,
        instruments, # [<Instrument>]
        since=None
    ):
        """Returns: list
        Get spread, in pips, for given currency pairs (e.g. 'USD_JPY%2CEUR_USD')
        """
        Log.write('oanda.py get_spreads()')
        prices = cls.get_prices(instruments, since)
        Log.write('prices:    \n{}'.format(prices))
        if prices == None:
            Log.write('oanda.py get_spreads(): Failed to get prices.')
            return None
        else:
            spreads = []
            for p in prices['prices']:
                # Oanda deprecated 'status' but 'tradeable' not used yet?
                tradeable = None
                try:
                    tradeable = p['tradeable']
                except:
                    try:
                        tradeable = ( p['status'] == 'tradeable' )
                    except:
                        tradeable = True
                spreads.append(
                    {
                        "instrument":p['instrument'],
                        "time":p['time'],
                        "spread":price_to_pips(p['instrument'], (float(p['asks'][0]['price']) - float(p['bids'][0]['price']))),
                        "tradeable":tradeable
                    }
                )
            return spreads


    @classmethod
    def place_order(cls, in_order):
        """Return type: dict
        Return value: information about the order (and related trade)
        Description: Place an order.

        If I place a trade that reduces another trade to closing, then I get a
        200 Code and information about the trade that closed. I.e. I don't get
        info about an opened trade.

        http://developer.oanda.com/rest-live-v20/order-df/#OrderRequest
        """
        Log.write ('"oanda.py" place_order(): Placing order...')
        request_body = { "order" : {} }
        # type
        request_body["order"]["type"] = in_order.order_type
        # instrument
        request_body["order"]["instrument"] = in_order.instrument.get_name()
        # units
        request_body["order"]["units"] = str(in_order.units)
        # time-in-force (market order)
        if in_order.order_type == "MARKET":
            request_body["order"]["timeInForce"] = "FOK"
        else:
            raise Exception # TODO
        # position fill
        request_body["order"]["positionFill"] = "DEFAULT"
        # stop loss
        if in_order.stop_loss != None:
            request_body["order"]["stopLossOnFill"] = in_order.stop_loss
        # take profit
        if in_order.take_profit != None:
            request_body["order"]["takeProfitOnFill"] = in_order.take_profit
        # trailing stop
        if in_order.trailing_stop != None:
            request_body["order"]["trailingStopLossOnFill"] = in_order.trailing_stop
        data = utils.stob( json.dumps( request_body ) ) # Oanda needs double quotes in JSON
        Log.write('oanda.py place_order(): data = {}'.format(data) )
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
            Log.write('"oanda.py" place_order(): Failed to place order 2nd time.')
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
        Log.write('oanda.py is_market_open()')
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
    WARNING: These are blatantly wrong, as they do not take into account
        Daylight Savings Time.
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
        total_delta_since_close = zero # default starting value
        for d in range(1,9): # eight days; market may close later today
            closes = cls.market_closes.get(day_iter)
            if closes != None:
                # There are closes this day.
                latest_close_to_now_delta = datetime.timedelta(days=1) # default starting value
                for c in closes:
                    if now_delta - c < latest_close_to_now_delta:
                        # make sure it's not a time later today
                        if d > 1 or now_delta > c:
                            # new potential most recent close
                            latest_close_to_now_delta = now_delta - c
                # Only return if a close earlier than now was found
                if latest_close_to_now_delta < datetime.timedelta(days=1):
                    total_delta_since_close += latest_close_to_now_delta
                    return total_delta_since_close
            day_iter -= 1 # move to previous day
            if day_iter < 1: # cycle
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
        

    @classmethod
    def get_transactions_since_id(
        cls,
        last_id, # string
    ):
        """Return type: dict
        Returns transactions since, but not including, last_id.
        """
        args = '?id={}'.format(last_id)
        transactions = cls.fetch(
             in_url='{}/v3/accounts/{}/transactions/sinceid{}'
            .format(Config.oanda_url, Config.account_id, args)
        )
        if not transactions:
            Log.write('oanda.py get_transactions_since_id(): result == None')
            raise Exception
        return transactions


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
        # NOTE: /v3/accounts/{accountID}/trades/{tradeSpecifier} 
        #   has a 'status' key  that can be used, if the reason is
        #   not needed.
        start = Timer.start()
        num_attempts = 2
        while num_attempts > 0:
            Log.write('"oanda.py" is_trade_closed(): Remaining attempts: ', str(num_attempts))
            transactions = cls.get_transactions_since_id(last_id=trade_id)
            #Log.write('oanda.py is_trade_closed(): transactions found:\n{}'.format(transactions))
            for transaction in transactions['transactions']:
                if 'type' in transaction:
                    if transaction['type'] == 'ORDER_FILL':
                        if 'tradesClosed' in transaction:   
                            for closed_trade in transaction['tradesClosed']:
                                if closed_trade['tradeID'] == trade_id:
                                    if 'reason' in transaction:
                                        reason = transaction['reason']
                                        Log.write('oanda.py is_trade_closed(): reason = {}'.format(reason))
                                        Timer.stop(start, 'Oanda.is_trade_closed()', 'xxx')
                                        if reason == 'LIMIT_ORDER':
                                            return (True, TradeClosedReason.LIMIT_ORDER)
                                        elif reason == 'STOP_ORDER':
                                            return (True, TradeClosedReason.STOP_ORDER)
                                        elif reason == 'MARKET_IF_TOUCHED_ORDER':
                                            return (True, TradeClosedReason.MARKET_IF_TOUCHED_ORDER)
                                        elif reason == 'TAKE_PROFIT_ORDER':
                                            return (True, TradeClosedReason.TAKE_PROFIT_ORDER)
                                        elif reason == 'STOP_LOSS_ORDER':
                                            return (True, TradeClosedReason.STOP_LOSS_ORDER)
                                        elif reason == 'TRAILING_STOP_LOSS_ORDER':
                                            return (True, TradeClosedReason.TRAILING_STOP_LOSS_ORDER)
                                        elif reason == 'MARKET_ORDER':
                                            return (True, TradeClosedReason.MARKET_ORDER)
                                        elif reason == 'MARKET_ORDER_TRADE_CLOSE':
                                            return (True, TradeClosedReason.MARKET_ORDER_TRADE_CLOSE)
                                        elif reason == 'MARKET_ORDER_POSITION_CLOSEOUT':
                                            return (True, TradeClosedReason.MARKET_ORDER_POSITION_CLOSEOUT)
                                        elif reason == 'MARKET_ORDER_MARGIN_CLOSEOUT':
                                            return (True, TradeClosedReason.MARKET_ORDER_MARGIN_CLOSEOUT)
                                        elif reason == 'MARKET_ORDER_DELAYED_TRADE_CLOSE':
                                            return (True, TradeClosedReason.MARKET_ORDER_DELAYED_TRADE_CLOSE)
                                        elif reason == 'LINKED_TRADE_CLOSED':
                                            return (True, TradeClosedReason.LINKED_TRADE_CLOSED)
                                        Log.write(
                                            'oanda.py is_trade_closed(): Unknown OrderFillReason: {}'
                                            .format(reason) )
                                        raise Exception
            num_attempts = num_attempts - 1
            # Delay to allow the trade to be processed on the dealer end
            time.sleep(1)
        Log.write('oanda.py is_trade_closed(): Unable to locate trade; possibly still open.')
        Timer.stop(start, 'Oanda.is_trade_closed()', 'unable to locate')
        return (False, None)


    @classmethod
    def get_open_trades(cls):
        """Return type: Instance of <Trades> or None
        Get info about all open trades
        """
        #Log.write('"oanda.py" get_open_trades(): Entering.')
        trades_oanda = cls.fetch('{}/v3/accounts/{}/openTrades'
            .format(Config.oanda_url,str(Config.account_id))
            )
        if trades_oanda == None:
            Log.write('"oanda.py" get_open_trades(): Failed to get trades from Oanda.')
            return None
        else:
            ts = Trades()
            for t in trades_oanda['trades']: 
                # format into a <Trade>
                ts.append(Trade(
                    units=t['initialUnits'],
                    broker_name = cls.__str__(),
                    instrument = Instrument(Instrument.get_id_from_name(t['instrument'])),
                    stop_loss = t['stopLossOrder']['price'],
                    strategy = None,
                    take_profit = t['takeProfitOrder']['price'],
                    trade_id = t['id']
                ))
            return ts


    @classmethod
    def get_trade(cls, trade_id):
        """Returns: <Trade> or None
        Get info about a particular trade.
        """
        trade_info = cls.fetch(
            '{}/v3/accounts/{}/trades/{}'.format(
                Config.oanda_url,
                str(Config.account_id),
                str(trade_id)
            )
        )
        try:
            trade = trade_info['trade']
            sl = None
            tp = None
            if 'stopLossOrder' in trade:
                sl = trade['stopLossOrder']['price']
            if 'takeProfitOrder' in trade:
                tp = trade['takeProfitOrder']['price']
            return Trade(
                units=trade['initialUnits'],
                broker_name = cls.__str__(),
                instrument = Instrument(Instrument.get_id_from_name(trade['instrument'])),
                stop_loss = sl,
                take_profit = tp,
                strategy = None,
                trade_id = trade['id']
            )
        except Exception:
            # Oanda returns 404 error if trade closed; don't raise Exception.
            Log.write('oanda.py get_trade(): Exception:\n{}'.format(sys.exc_info()))
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
        stop_loss_price=None,
        trailing_stop_loss_distance=None
    ):
        """Returns:
        This is trimmed down from Oanda's v20 API.
        """
        #Log.write('"oanda.py" modify_trade(): Entering.')

        request_body = {}
        if take_profit_price:
            request_body['takeProfit'] = {'price':take_profit_price}
        if stop_loss_price:
            request_body['stopLoss'] = {'price':stop_loss_price}
        if trailing_stop_loss_distance:
            request_body['trailingStopLoss'] = {'distance':trailing_stop_loss_distance}

        response = cls.fetch(
            in_url='{}/v3/accounts/{}/trades/{}/orders'
            .format(
                Config.oanda_url,
                Config.account_id,
                str(trade_id)
            ),
            in_data=utils.stob( # Oanda needs double quotes
                json.dumps(request_body)
            ),
            in_method='PUT'
        )
        if response != None:
            return response
        else:
            Log.write('"oanda.py" modify_trade(): Failed to modify trade.')
            return None



"""
File:           daemon.py
Python version: Python 3.4
Description:    Main function.
"""

# standard libraries
import atexit
import curses
import datetime
import json
import sys
import time         # for sleep()
#import urllib.request
#import urllib.error

"""# private strategy modules
try:
    sys.path.index('/home/user/raid/documents/algo/private_strategies')
except ValueError:
    sys.path.append('/home/user/raid/documents/algo/private_strategies')
from blah import blah """

from broker import Broker
from config import Config
from db import DB
from instrument import Instrument
from log import Log
from oanda import Oanda
from opportunity import *
from order import *
from strategies.fifty import *
from timer import Timer


class Daemon():
    """
    The daemon:
      - Manages account balance, margin, risk.
      - Accepts and rejects trade opportunities.
      - Forcefully close trades as needed (e.g. during shutdown)
    """

    # Initialize log.
    Log.clear()

    # diagnostic info
    DB.execute('INSERT INTO startups (timestamp) VALUES (NOW())')

    # flag to shut down
    stopped = False    

    # opportunity pool
    opportunities = Opportunities()

    # Specify the backup strategy.
    backup_strategy = Fifty 

    """
    Set the strategies to use.
    If backup_strategy is different than the other strategies, be sure to
        add that too. Otherwise you don't need to add it again.
    """
    strategies = []
    strategies.append(Fifty)
    #strategies.append(backup_strategy)

    msg_base = '' # user interface template


    @classmethod
    def num_strategies_with_positions(cls):
        sum = 0
        for s in cls.strategies:
            if s.get_number_positions() > 0:
                sum += 1
        return sum


    @classmethod
    def num_strategies_with_no_positions(cls):
        return len(cls.strategies) - cls.num_strategies_with_positions()


    @classmethod
    def _curses_init(cls, stdcsr):
        # initialize curses
        curses.echo()   # echo key presses
        stdcsr.nodelay(1) # non-blocking window
        stdcsr.clear() # clear screen
        cls.msg_base = '\n'
        if Config.live_trading:
            cls.msg_base += 'LIVE TRADING\n'
        else:
            cls.msg_base += 'Simulation.\n'
        cls.msg_base += 'Press q to shut down.\n'
        cls.msg_base += 'Press m to monitor.\n\n'
        cls.msg_base += 'Account balance: {}\n'
        cls.msg_base += '>'
        stdcsr.addstr(cls.msg_base)
        stdcsr.refresh() # redraw


    """
    refresh user interface
    TODO: this waits for the REST calls to return. Too slow.
    """
    @classmethod
    def _curses_refresh(cls, stdcsr):
        ch = stdcsr.getch() # get one char
        if ch == 113: # q == quit
            stdcsr.addstr('\nInitiating shutdown...\n')
            stdcsr.refresh() # redraw
            curses.nocbreak()
            stdcsr.keypad(False)
            #curses.echo()   
            curses.endwin() # restore terminal
            cls.shutdown()
        elif ch == 109: # m == monitor
            account_id = Config.account_id
            balance = Broker.get_balance(account_id)
            msg = cls.msg_base.format(balance)
            stdcsr.clear()
            stdcsr.addstr(msg)
            stdcsr.refresh() # redraw


    @classmethod
    def run(cls, stdcsr):
        """Returns: void
        This is the main program loop.
        """
        # initialize user interface
        cls._curses_init(stdcsr)

        # Read in existing trades
        while not cls.stopped and cls.recover_trades() == None:
            Log.write('"daemon.py" run(): Recovering trades...')
            cls._curses_refresh(stdcsr)

        # logging
        if Config.live_trading:
            Log.write('"daemon.py" start(): Using live account.')
        else:
            Log.write('"daemon.py" start(): Using practice mode.')

        """
        Main loop:
        1. Gather opportunities from each strategy.
        2. Decide which opportunities to execute.
        3. Clear the opportunity list.
        """
        while not cls.stopped:
            # refresh user interface
            cls._curses_refresh(stdcsr)

            # Let each strategy suggest an order
            for s in cls.strategies:
                new_opp = s.refresh()
                if new_opp == None:
                    Log.write('daemon.py run(): refresh() failed for {}.'
                        .format(s.get_name()))
                    raise Exception
                elif new_opp == []:
                    Log.write('daemon.py run(): {} has nothing to offer now.'
                        .format(s.get_name()))
                    pass
                else:
                    cls.opportunities.push(new_opp)
        
            # Decide which opportunity (or opportunities) to execute
            Log.write('"daemon.py" run(): Picking best opportunity...')
            best_opp = cls.opportunities.pick()
            if best_opp == None:
                # Nothing is being suggested.
                pass
            else:
                # An order was suggested by a strategy, so place the order.
                #   Don't use all the money available.
                SLIPPAGE_WIGGLE = 0.95
                ###available_money = Broker.get_margin_available(Config.account_id) * SLIPPAGE_WIGGLE
                available_money = 100 # USD - testing
                #   Get the current price of one unit.
                instrument_price = 0
                go_long = best_opp.order.units > 0
                if go_long:
                    instrument_price = Broker.get_ask(best_opp.order.instrument)
                else:
                    instrument_price = Broker.get_bid(best_opp.order.instrument)
                #   How much leverage available:
                margin_rate = Broker.get_margin_rate(best_opp.order.instrument) 
                #   TODO: A bit awkward, but overwrite the existing value that was used to 
                #   determine long/short.
                units = available_money
                units /= cls.num_strategies_with_no_positions() # save money for other strategies
                units /= margin_rate
                units = int(units) # floor
                if units <= 0: # verify
                    Log.write('daemon.py run(): units <= 0')
                    raise Exception # abort
                if not go_long: # negative means short
                    units = -units
                best_opp.order.units = units
                Log.write('daemon.py run(): Executing opportunity:\n{}'.format(best_opp))
                order_result = Broker.place_order(best_opp.order)
                # Notify the strategies.
                if 'orderFillTransaction' in order_result:
                    try:
                        opened_trade_id = order_result['orderFillTransaction']['tradeOpened']['tradeID']
                        best_opp.strategy.trade_opened(trade_id=opened_trade_id)
                    except:
                        Log.write(
                            'daemon.py run(): Failed to extract opened trade from order result:\n{}'
                            .format(order_result) )
                        raise Exception
                elif 'tradesClosed' in order_result:
                    try:
                        for trade in order_result['orderFillTransaction']['tradesClosed']:
                            best_opp.strategy.trade_closed(trade_id=trade['tradeID'])
                    except:
                        Log.write(
                            'daemon.py run(): Failed to extract closed trades from order result:\n{}'
                            .format(order_result) )
                        raise Exception
                elif 'tradeReduced' in order_result:
                    try:
                        closed_trade_id = order_result['orderFillTransaction']['tradeReduced']['tradeID']
                        best_opp.strategy.trade_reduced(
                            closed_trade_id,
                            instrument_id=Instrument.get_id_from_name(order_result['instrument'])
                        )
                    except:
                        Log.write(
                            'daemon.py run(): Failed to extract reduced trades from order result:\n{}'
                            .format(order_result) )
                        raise Exception
                else:
                    Log.write(
                        '"daemon.py" run(): Unrecognized order result:\n{}'
                        .format(order_result) )
                    raise Exception

            """
            Clear opportunity list.
            Opportunities should be considered to exist only in the moment,
            so there is no need to save them for later.
            """
            cls.opportunities.clear()
        """
        Shutdown stuff. This runs after shutdown() is called, and is the
        last code that runs before returning to algo.py.
        """
        DB.shutdown()  # atexit() used in db.py, but call to be safe.


    @classmethod
    def shutdown(cls):
        """
        Stop daemon.
        TODO:
            * set SL and TP
            * write diagnostic info to db
        """
        Log.write('"daemon.py" shutdown(): Shutting down daemon.')
        cls.stopped = True
        

    @classmethod
    def recover_trades(cls):
        """Returns: None on failure, any value on success
        See if there are any open trades, and resume babysitting.
        -
        If trades are opened without writing their info to the db,
        the trade cannot be distributed back to the strategy that opened
        it, because it is unknown what strategy placed the order.
        This could be solved by writing to the db before placing the order,
        synchronously. However if placing the order failed, then the database
        record would have to be deleted, and this would be messy.
        Instead, designate a backup strategy that adopts orphan trades.
        """

        # Get trades from broker.
        open_trades_broker = Broker.get_open_trades() # instance of <Trades>
        if open_trades_broker == None:
            Log.write('daemon.py recover_trades(): Broker.get_open_trades() failed.')
            return None 

        # Delete any trades from the database that are no longer open.
        #   First, ignore trades that the broker has open.
        db_trades = DB.execute('SELECT trade_id FROM open_trades_live')
        Log.write('"daemon.py" recover_trades():\ndb open trades: {}\nbroker open trades: {}'
            .format(db_trades, open_trades_broker))
        for index, dbt in enumerate(db_trades): # O(n^3)
            for otb in open_trades_broker:
                if str(dbt[0]) == str(otb.trade_id): # compare trade_id
                    del db_trades[index]
        #   The remaining trades are in the "open trades" db table, but 
        #   the broker is not listing them as open.
        #   They may have closed since the daemon last ran; confirm this.
        #   Another cause is that trades are automatically removed from
        #   Oanda's history after much time passes.
        for dbt in db_trades:
            if Broker.is_trade_closed(dbt[0])[0]:
                # Trade is definitely closed; update db.
                Log.write('"daemon.py" recover_trades(): Trade {} is closed. Deleting from db.'
                    .format(dbt[0]))
            else:
                # Trade is in "open trades" db table and the broker
                # says the trade is neither open nor closed.
                DB.bug('Trade w/ID ({}) is neither open nor closed.'
                    .format(dbt[0]))
                Log.write('"daemon.py" recover_trades(): Trade w/ID (',
                    '{}) is neither open nor closed.'.format(dbt[0]))
            DB.execute('DELETE FROM open_trades_live WHERE trade_id="{}"'
                .format(dbt[0]))
            
        """
        Fill in info not provided by the broker, e.g.
        the name of the strategy that opened the trade.

        It's possible that a trade will be opened then the system is
        unexpectedly terminated before info about the trade can be saved to
        the database. Thus a trade may not have a corresponding trade in the database.
        """
        for i in range(0,len(open_trades_broker)):
            broker_trade = open_trades_broker[i]
            db_trade_info = DB.execute(
                'SELECT strategy, broker FROM open_trades_live WHERE trade_id="{}"'
                .format(broker_trade.trade_id)
            )
            if len(db_trade_info) > 0:
                # Verify broker's info and database info match, just to be safe.
                # - broker name
                if db_trade_info[0][1] != broker_trade.broker_name:
                    Log.write('"daemon.py" recover_trades(): ERROR: "{}" != "{}"'
                        .format(db_trade_info[0][1], broker_trade.broker_name))
                    raise Exception
                # set strategy
                broker_trade.strategy = None # TODO: use a different default?
                for s in cls.strategies:
                    if s.get_name == db_trade_info[0][0]:
                        broker_trade.strategy = s # reference to class instance
            else:
                # Trade in broker but not db.
                # Maybe the trade was opened manually. Ignore it.
                # Remove from list.
                open_trades_broker = open_trades_broker[0:i] + open_trades_broker[i+1:len(open_trades_broker)] # TODO: optimize speed

        # Distribute trades to their respective strategy modules
        for broker_trade in open_trades_broker:
            if broker_trade.strategy != None:
                # Find the strategy that made this trade and notify it.
                for s in cls.strategies:
                    if broker_trade.strategy.get_name() == s.get_name(): 
                        s.recover_trade(broker_trade.trade_id)
                        open_trades_broker.remove(broker_trade.trade_id)
                        break
            else:
                # It is not known what strategy opened this trade.
                # One possible reason is that the strategy that opened the
                # trade is no longer open.
                # Assign it to the backup strategy.
                Log.write('"daemon.py" recover_trades(): Assigning trade ',
                    ' ({}) to backup strategy ({}).'
                    .format(broker_trade.trade_id, cls.backup_strategy.get_name()))
                cls.backup_strategy.recover_trade(broker_trade.trade_id)
        return 0 # success
                

# There are not destructors in Python, so use this.
atexit.register(Daemon.shutdown)


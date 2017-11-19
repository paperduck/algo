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

# private strategy modules
try:
    sys.path.index('/home/user/raid/documents/algo/private_strategies')
except ValueError:
    sys.path.append('/home/user/raid/documents/algo/private_strategies')
from follow_trend import FollowTrend

# project modules
from broker import Broker
from config import Config
from db import DB
from log import Log
from oanda import Oanda
from opportunity import *
from order import *
from strategies.fifty import *
from timer import Timer


# Limitations should be specified here, such as 
#   which instruments to use
#   number of units
#   amount of capital to use
# The daemon:
#   - Manages account balance, margin, risk.
#   - Accepts and rejects trade opportunities.
#   - Forcefully close trades as needed (e.g. during shutdown)
class Daemon():
    """
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

    # Set the strategies to use.
    # If backup_strategy is different than the other
    # strategies, be sure to add that too. If it matches one of
    # the strategies you will use, then don't add it.
    strategies = []
    strategies.append(Fifty)
    #strategies.append(FollowTrend)
    #strategies.append(backup_strategy)


    @classmethod
    def run(cls, stdcsr):
        """
        """
        # initialize curses
        curses.echo()   # echo key presses
        stdcsr.nodelay(1) # non-blocking window
        stdcsr.clear() # clear screen
        msg_base = '\n'
        if Config.live_trading:
            msg_base += 'LIVE TRADING\n'
        else:
            msg_base += 'Simulation.\n'
        msg_base += 'Press q to shut down.\n'
        msg_base += 'Press m to monitor.\n\n'
        msg_base += 'Account balance: {}\n'
        msg_base += '>'
        stdcsr.addstr(msg_base)
        stdcsr.refresh() # redraw

        # Read in existing trades
        Log.write('"daemon.py" run(): Recovering trades...')
        cls.recover_trades()

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

            # curses
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
                acct = Oanda.get_account_primary()
                msg = msg_base.format(acct['balance'])
                stdcsr.clear()
                stdcsr.addstr(msg)
                stdcsr.refresh() # redraw
                

            # Let each strategy suggest an order
            # TODO: Let strategies suggest multiple orders
            for s in cls.strategies:
                new_opp = s.refresh()
                if new_opp == None:
                    Log.write('"daemon.py" run(): refresh() failed for {}.'
                        .format(s.get_name()))
                elif new_opp == []:
                    # Strategy has nothing to offer at the moment.
                    Log.write('"daemon.py" run(): {} has nothing to offer '
                        'now.'.format(s.get_name()))
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
                # Place the order.
                order_result = Broker.place_order(best_opp.order)
                Log.write('"daemon.py" run(): order_result = \n{}'
                    .format(order_result))
                if order_result['tradeOpened'] != {}:
                    # Notify the strategy.
                    best_opp.strategy.trade_opened(
                        trade_id=order_result['tradeOpened']['id'],
                        instrument_id=4
                    )
                elif order_result['tradesClosed'] != []:
                    for tc in order_result['tradesClosed']:
                        # Notify the strategy.
                        best_opp.strategy.trade_closed(
                            trade_id=tc['id'],
                            instrument_id=4
                        )
                elif order_result['tradeReduced'] != {}:
                    # Notify the strategy.
                    best_opp.strategy.trade_reduced(
                        order_result['tradeReduced']['id'],
                        instrument_id=4
                    )
                else:
                    # catch-all for formality
                    Log.write('"daemon.py" run(): Unknown trade result.')
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
        pass


    @classmethod
    def shutdown(cls):
        """
        Stop daemon.
        TODO:
            * set SL and TP
            * write diagnostic info to db
        """
        Log.write('"daemon.py" shutdown(): Shutting down daemon.')
        DB.shutdown()  # atexit() used in db.py, but call to be safe.
        cls.stopped = True
        

    @classmethod
    def recover_trades(cls):
        """
        See if there are any open trades, and resume babysitting.

        If trades are opened without writing their info to the db,
        the trade cannot be distributed back to the strategy that opened
        it, because it is unknown what strategy placed the order.
        This could be solved by writing to the db before placing the order,
        synchronously. However if placing the order failed, then the database
        record would have to be deleted, and this would be messy.
        Instead, designate a backup strategy that adopts orphan trades.
        """
        Log.write('"daemon.py" recover_trades(): Entering.')
        # Get trades from broker.
        open_trades_broker = Broker.get_trades() # instance of <Trades>

        # Delete any trades from the database that are no longer open.
        # First, ignore trades that the broker has open.
        db_trades = DB.execute('SELECT trade_id FROM open_trades_live')
        Log.write('"daemon.py" recover_trades():\ndb open trades: {}\nbroker open trades: {}'
            .format(db_trades, open_trades_broker))
        for dbt in db_trades: # O(n^3)
            for otb in open_trades_broker:
                if str(dbt[0]) == str(otb.trade_id):
                    # same trade_id
                    db_trades.remove(dbt)
        # The remaining trades are in the "open trades" db table, but 
        # the broker is not listing them as open.
        # They may have closed since the daemon last ran; confirm this.
        # Another cause is that trades are automatically removed from
        # Oanda's history after much time passes.
        for dbt in db_trades:
            if Broker.is_trade_closed(dbt[0])[0]:
                # Trade is definitely closed; update db.
                Log.write('"daemon.py" recover_trades(): Trade {} is closed. Deleting from db.'
                    .format(dbt[0]))
                DB.execute('DELETE FROM open_trades_live WHERE trade_id="{}"'
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
        #for t in open_trades_broker:
        for i in range(0,len(open_trades_broker)):
            t = open_trades_broker[i]
            trade_info = DB.execute('SELECT strategy, broker, instrument_id FROM open_trades_live WHERE trade_id="{}"'
                .format(t.trade_id))
            if len(trade_info) > 0:
                # Verify broker's info and database info match, just to be safe.
                # - broker name
                if trade_info[0][1] != t.broker_name:
                    Log.write('"daemon.py" recover_trades(): ERROR: "{}" != "{}"'
                        .format(trade_info[0][1], t.broker_name))
                    raise Exception
                # - instrument/symbol
                instrument = DB.execute('SELECT symbol FROM instruments WHERE id="{}"'
                    .format(trade_info[0][2]))
                if instrument[0][0] != t.instrument:
                    Log.write('"daemon.py" recover_trades): {} != {}'
                        .format(instrument[0][0], t.instrument))
                    raise Exception
                # set strategy
                t.strategy = None
                for s in cls.strategies:
                    if s.get_name == trade_info[0][0]:
                        t.strategy = s # reference to class instance
            else:
                # Trade in broker but not db.
                # Maybe the trade was opened manually. Ignore it.
                # Remove from list.
                open_trades_broker = open_trades_broker[0:i] + open_trades_broker[i+1:len(open_trades_broker)] # TODO: optimize speed

        # Distribute trades to their respective strategy modules
        for t in open_trades_broker:
            if t.strategy != None:
                # Find the strategy that made this trade and notify it.
                for s in cls.strategies:
                    if t.strategy.get_name() == s.get_name(): 
                        s.recover_trade(trade)
                        open_trades_broker.remove(t.trade_id)
                        break
            else:
                # It is not known what strategy opened this trade.
                # One possible reason is that the strategy that opened the
                # trade is no longer open.
                # Assign it to the backup strategy.
                Log.write('"daemon.py" recover_trades(): Assigning trade ',
                    ' ({}) to backup strategy ({}).'
                    .format(t.trade_id, cls.backup_strategy.get_name()))
                cls.backup_strategy.recover_trade(t)
                

# There are not destructors in Python, so use this.
atexit.register(Daemon.shutdown)


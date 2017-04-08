"""
File:           daemon.py
Python version: Python 3.4
Description:    Main function.
"""

#*************************
import curses
import datetime
import json
import sys
import time         # for sleep()
#import urllib.request
#import urllib.error
#*************************
from broker import Broker
from db import DB
from log import Log
from opportunity import *
from order import *
from strategies.fifty import *
from timer import Timer
from trade import *
#*************************

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
    Log.write( datetime.datetime.now().strftime("%c") + "\n\n" )

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
    #strategies.append(backup_strategy)


    @classmethod
    def __del__(cls):
        """
        """
        #cls.stop() TODO: too late for this?
        pass


    @classmethod
    def run(cls, stdcsr):
        """
        """
        # curses
        curses.echo()   # echo key presses
        stdcsr.nodelay(1) # non-blocking window
        stdcsr.clear() # clear screen
        stdcsr.addstr('Press q to shut down.')

        Log.write('"daemon.py" run(): Recovering trades...')
        # Read in existing trades
        cls.recover_trades()
        if Broker.is_practice():
            Log.write('"daemon.py" start(): Using practice mode.')
        else:
            Log.write('"daemon.py" start(): Using live account.')

        """
        Main loop:
        1. Gather opportunities from each strategy.
        2. Decide which opportunities to execute.
        3. Clear the opportunity list.
        """
        while not cls.stopped:
            # curses
            ch = stdcsr.getch() # get one char
            if ch == 113: # q
                stdcsr.addstr('\n!!! Initiating shutdown... !!!\n')
                stdcsr.refresh() # redraw
                curses.nocbreak()
                stdcsr.keypad(False)
                #curses.echo()   
                curses.endwin() # restore terminal
                cls.stopped = True
                DB.shutdown()
                

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
                if order_result == None:
                    # Failed to place order.
                    Log.write('"daemon.py" run(): Failed to place order.')
                else:
                    # Order was placed.
                    # Notify the strategy.
                    # TODO: This notification code is specific to Oanda.
                    if order_result['tradeOpened'] != {}:
                        Log.write('"daemon.py" run(): order_result = \n{}'
                            .format(order_result))
                        best_opp.strategy.trade_opened(
                            order_result['tradeOpened']['id']
                        )
                    elif order_result['tradesClosed'] != []:
                        for tc in order_result['tradesClosed']:
                            best_opp.strategy.trade_closed(tc['id'])
                    elif order_result['tradeReduced'] != {}:
                        best_opp.strategy.trade_reduced(
                            order_result['tradeReduced']['id']
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


    @classmethod
    def shutdown(cls):
        """
        Stop daemon.
        TODO:
            * set SL and TP
            * write diagnostic info to db
        """
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
        if open_trades_broker == None:
            Log.write('"daemon.py" recover_trades(): Failed to get list of trades. ABORTING')
            cls.stop()
            #sys.exit()

        # Fill in strategy info
        open_trades_broker.fill_in_trade_extra_info()

        # Distribute trades to their respective strategy modules
        for trade in open_trades_broker:
            if trade.strategy != None:
                # Find the strategy that made this trade and notify it.
                for s in cls.strategies:
                    if trade.strategy.get_name() == s.get_name(): 
                        s.recover_trade(trade)
                        open_trades_broker.pop(trade.trade_id)
                        break
            else:
                # It is not known what strategy opened this trade.
                Log.write('"daemon.py" recover_trades(): Trade\'s strategy unknown. Checking if closed.')
                if Broker.is_trade_closed(trade.trade_id):
                    # The trade has closed, so I don't need to track it any
                    # more.
                    Log.write('"daemon.py" recover_trades(): This trade has\
                        closed since daemon last ran:\n{}\n'\
                        .format(t.trade_id))
                    pass # TODO: write something to the database
                else:
                    # The trade is open, but I don't know which strategy
                    # opened it. Assign it to the backup strategy.
                    Log.write('"daemon.py" recover_trades(): Trade with ',
                        'unknown state:\n{}\n'.format(trade))
                    Log.write('"daemon.py" recover_trades(): Assigning trade ',
                        'to backup strategy ({}).'.format(cls.backup_strategy.get_name()))
                    cls.backup_strategy.recover_trade(trade)
                



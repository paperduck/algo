#!/usr/bin/python3

# daemon.py
# main function for algo daemon 
# Python 3.4

#*************************
import datetime
import json
import sys
import time         # for sleep()
#import urllib.request
#import urllib.error
#*************************
from strategies.fifty import *
from log import *
from broker import *
from opportunity import *
from order import *
from trade import *
#*************************

# Limitations should be specified here, such as 
#   which instruments to use
#   number of units
#   amount of capital to use
# The daemon:
#   - Manages account balance, margin, risk.  Can block trades to protect these.
#   - Forcefully close trades as needed (e.g. shutdown)
class Daemon():
    
    def __init__(self):
        """
        """
        self.stopped = False    # flag to stop running    
        self.opportunities = Opportunities()
        self.strategies = []

        log.clear()
        log.write( datetime.datetime.now().strftime("%c") + "\n\n" )

        # Specify which trategies to run.
        self.strategies.append( Fifty() )

        # Read in existing trades
        self.recover_trades()


    def __del__(self):
        """
        """
        #self.stop() TODO: too late for this?
        pass


    def start(self):
        """
        """
        log.write('Daemon starting.')
        if Broker.is_practice():
            log.write('"daemon.py" start(): Using practice mode.')
        else:
            log.write('"daemon.py" start(): Using live account.')

        # Loop:
        """
        1. Gather opportunities from each strategy.
        2. Decide which opportunities to execute.
        3. Clear the opportunity list.
        """
        while not self.stopped:
            # Let each strategy suggest an order
            # TODO: Let strategies suggest multiple orders
            for s in self.strategies:
                new_opp = s.refresh()
                if new_opp == None:
                    # Strategy has nothing to offer at the moment.
                    pass
                else:
                    self.opportunities.push(new_opp)
        
            # Decide which opportunities to execute
            order_result = Broker.place_order(self.opportunities.pop().order)
            if order_result == None:
                s.callback( False, new_order )
                log.write('"daemon.py" start(): Failed to place order.')
            else:
                trade = order_result['tradeOpened']
                # TODO: Oanda: If I place a trade that reduces another trade to closing, then I get a 
                # 200 Code and information about the trade that closed. I.e. I don't get 
                # info about an opened trade. (Oanda)
                new_order.transaction_id = trade['id']
                # TODO write trade info my database
                """
                It's possible that a trade will be opened, then the system is
                terminated before the trade is written to the database.
                """

            # Clear opportunity list.
            # Opportunities should be considered to exist only in the moment,
            # so there is no need to save them for later.
            self.opportunities = []


    def stop(self):
        """
        stop daemon; tidy up open trades
        """
        self.stopped = True


    def recover_trades(self):
        """
        See if there are any open trades.
        """
        # Get trades from broker.
        open_trades_broker = Broker.get_trades() # instance of `trades`
        if open_trades_broker == None:
            log.write('"daemon.py" __init__(): Failed to get list of trades. ABORTING')
            sys.exit()

        # Fill in strategy info
        open_trades_broker.fill_in_trade_extra_info()

        # Distribute trades to their respective strategy modules
        for i in range(0, (open_trades_broker.length())-1):
            if open_trades_broker[i].strategy_name != None:
                # find the strategy that made this trade and notify it.
                for s in self.strategies:
                    if open_trades_broker[i].strategy_name == s.name:
                        s.callback_recover_trade(open_trades_broker[i])
                        open_trades_broker.pop(i)

        # See if there were any trades that were not distributed back to their
        # strategy.
        unknown_state = False
        for t in open_trades_broker:
            if broker.is_trade_closed(t.transaction_id):
                # Trade closed; don't need to track it any more; no problem.
                log.write('"daemon.py" recover_trades(): This trade has closed\
                           since daemon last ran:\n{}\n'.format(str(t)))
                pass
            else:
                # Trade hasn't closed, but the broker is not aware of a matching
                # live trade. Problem!
                log.write('"daemon.py" recover_trades(): Trade with unknown \
                           state:')
                log.write(str(t))
                log.write('~')
                unknown_state = True
        if unknown_state:
            log.write('"daemon.py" recover_trades(): Aborting due to trade \
                       with unknown state.')
            sys.exit()


if __name__ == "__main__":
    d = Daemon()
    d.start()


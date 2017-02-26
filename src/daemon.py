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
from broker import *
from log import *
from opportunity import *
from order import *
from strategies.fifty import *
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
        self.backup_babysitter = BackupBabysitter()

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
        
            # Decide which opportunity (or opportunities) to execute
            best_opp = self.opportunities.pick()
            if best_opp == None:
                # Nothing is being suggested.
                pass
            else:
                # Place the order.
                order_result = Broker.place_order(best_opp.order)
                if order_result == None:
                    # Failed to place order.
                    log.write('"daemon.py" start(): Failed to place order.')
                else:
                    # Order was placed.
                    trade = order_result['tradeOpened'] # could be tradeClosed instead
                    new_order.transaction_id = trade['id']
                    # TODO: Write trade info to database

            # Clear opportunity list.
            # Opportunities should be considered to exist only in the moment,
            # so there is no need to save them for later.
            self.opportunities.clear()


    def stop(self):
        """
        stop daemon; tidy up open trades
        """
        self.stopped = True


    def recover_trades(self):
        """
        See if there are any open trades, and start babysitting them again.

        If trades are opened without writing their info to the db,
        the trade cannot be distributed back to the strategy that opened
        it, because it is unknown what strategy placed the order.
        This could be solved by writing to the db before placing the order,
        synchronously. However if placing the order failed, then the database
        record would have to be deleted, and this would be messy.
        Instead, have a generic "nanny" function that takes care of "orphan"
        trades instead of a particular strategy; a "backup babysitter".
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
                # Find the strategy that made this trade and notify it.
                for s in self.strategies:
                    if open_trades_broker[i].strategy_name == s.name:
                        s.recover_trade(open_trades_broker[i])
                        open_trades_broker.pop(i)
            else:
                # It is not known what strategy opened this trade.
                if broker.is_trade_closed(t.transaction_id):
                    # The trade has closed, so I don't need to track it any
                    # more.
                    log.write('"daemon.py" recover_trades(): This trade has\
                        closed since daemon last ran:\n{}\n'.format(str(t)))
                    pass # TODO
                else:
                    # The trade is open, but I don't know which strategy
                    # opened it. Assign it to the "backup babysitter".
                    # TODO
                    log.write('"daemon.py" recover_trades(): Trade with unknown \
                        state:\n{}\n'.format(str(t)))
                    log.write('"daemon.py" recover_trades(): Assigning trade to\
                        backup babysitter.')
                    self.backup_babysitter.adopt(t)
                

if __name__ == "__main__":
    d = Daemon()
    d.start()


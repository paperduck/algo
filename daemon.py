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
import fifty
from logger import log
from broker import broker
from opportunity import *
import order
from trade import trade
#*************************

# Limitations should be specified here, such as 
#   which instruments to use
#   number of units
#   amount of capital to use
# The daemon:
#   - Manages account balance, margin, risk.  Can block trades to protect these.
#   - Forcefully close trades as needed (e.g. shutdown)
class daemon():
    
    def __init__(self):
        """
        """
        self.stopped = False    # flag to stop running    
        self.opportunities = opportunities()
        self.strategies = []

        log.clear()
        log.write( datetime.datetime.now().strftime("%c") + "\n\n" )

        # Read in existing trades
        open_trades = broker.get_trades() # get list of `trade` objects
        if trades == None:
            log.write('"daemon.py" __init__(): Failed to get list of trades. ABORTING')
            sys.exit()
        else:
            # Distribute tasks to their respective strategy modules
            # TODO Query db: Get strategy that opened each trade.
            pass

        # Specify which trategies to run.
        self.strategies.append( fifty.fifty() ) 


    def __del__(self):
        """
        """
        #self.stop() TODO: too late for this?
        pass

  
    def start(self):
        """
        """
        log.write('Daemon starting.')
        if broker.is_practice():
            log.write('Using practice mode.')
        else:
            log.write('Using live account.')

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
                    self.opportunities.append( new_opp )
        
            # Decide which opportunities to execute
            order_result = broker.place_order( self.opportunities.pop().order )
            if order_result == None:
                s.callback( False, new_order )
                log.write('"daemon.py" start(): Failed to place order.')
            else:
                trade = order_result['tradeOpened']
                # TODO: Oanda: If I place a trade that reduces another trade to closing, then I get a 
                # 200 Code and information about the trade that closed. I.e. I don't get 
                # info about an opened trade. (Oanda)
                new_order.transaction_id = trade['id']

            # Clear opportunity list.
            # Opportunities should be considered to exist only in the moment,
            # so there is no need to save them for later.
            self.opportunities = []


    def stop(self):
        """
        stop daemon; tidy up open trades
        """
        self.stopped = True


if __name__ == "__main__":
    d = daemon()
    d.start()


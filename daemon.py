#!/usr/bin/python3

# daemon.py
# main function for algo daemon 
# Python 3.4

#--------------------------
import datetime
import json
import sys
import time         # for sleep()
#import urllib.request
#import urllib.error
#--------------------------
#import entrance #TODO use this
import fifty
from log import log
from oanda import oanda
import order
import trade
#--------------------------

# Limitations should be specified here, such as 
#   which instruments to use
#   number of units
#   amount of capital to use
# The daemon:
#   - Manages account balance, margin, risk.  Can block trades to protect these.
#   - Forcefully close trades as needed
class daemon():
    
    #
    def __init__(self):
        self.orders = []        # list of open orders
        self.stopped = False    # flag to stop running    
        log.clear()
        log.write( datetime.datetime.now().strftime("%c") + "\n\n" )

        # Read in existing trades
        self.preexisting_trades = []
        trades = oanda.get_trades()
        if trades == None:
            log.write('"daemon.py" __init__(): Failed to get list of trades. ABORTING')
            sys.exit()
        else:
            for t in trades['trades']:
                self.preexisting_trades.append( trade.trade( t['id'], t['instrument'] ) )

        # strategies to run
        self.strategies = []
        log.write('"daemon.py" __init__(): Appending 50/50 strategy.')
        self.strategies.append( fifty.fifty( self.preexisting_trades ) )

    # 
    def __del__(self):
        self.stop()
  
    #
    def start(self):
        log.write('Daemon starting.')
        self.stopped = False
        if oanda.is_practice():
            log.write('Using practice mode.')
        else:
            log.write('Using live account.')

        # Loop:
        log.write('Entering main daemon loop.')
        while not self.stopped:
            # Let the strategies update themselves
            for s in self.strategies:
                # See if the strategy has anything to offer
                new_order = s.refresh()
                if new_order != None:
                    # The strategy has suggested an order, so attempt to place the order.
                    #log.write('"daemon.py" in start(): Attempting to place order.')
                    order_result = oanda.place_order( new_order )
                    # TODO Check if the order failed, call the strategy's callback function 
                    if order_result == None:
                        s.callback( False, new_order )
                        log.write('"daemon.py" start(): Failed to place order.')
                    else:
                        #new_order.transaction_id = order_result['tradeOpened']['id']
                        trade = order_result['tradeOpened']
                        # TODO: If I place a trade that reduces another trade to closing, then I get a 
                        # 200 Code and information about the trade that closed (no trade opened!)
                        new_order.transaction_id = trade['id']
                        s.callback( True, new_order )
                else:
                    # Strategy has nothing to offer at the moment.
                    #log.write('daemon.py: daemon.start(): Strategy "', str(s), '" placed no new orders.')
                    pass
            # limit API request frequency
            #log.write('daemon.py: start(): Sleeping.')
            #time.sleep(1)
    # stop daemon; tidy up open trades
    def stop(self):
        self.stopped = True


if __name__ == "__main__":
    d = daemon()
    d.start()


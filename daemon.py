#!/usr/bin/python3

# daemon.py
# main function for algo daemon 
# Python 3.4

#--------------------------
import datetime
#import sys
#import urllib.request
#import urllib.error
import time         # for sleep()
#from jq import jq
import json
#--------------------------
import oanda
#import entrance #TODO use this
import log as loggy
import fifty
import order
#--------------------------

# Limitations should be specified here, such as 
#   which instruments to use
#   number of units
#   amount of capital to use
# The daemon:
#   - Manages account balance, margin, risk.  Can block trades to protect these.
#   - Forcefully close trades as needed
class daemon():
    
    def __init__(self):
        self.orders = []        # list of open orders
        self.stopped = False    # flag to stop running    
        self.log = loggy.log(True)
        self.log.clear()
        self.log.write( datetime.datetime.now().strftime("%c") + "\n\n" )
        self.oanda_instance = oanda.oanda()

        # strategies to run
        self.strategies = []
        self.log.write('In daemon: Appending 50/50 strategy.')
        self.strategies.append( fifty.fifty() )


    def start(self):
        self.log.write('Daemon starting.')
        self.stopped = False
        if self.oanda_instance.practice:
            self.log.write('Using practice mode.')
        else:
            self.log.write('Using live account.')

        # Loop:
        #   
        self.log.write('Entering main daemon loop.')
        while not self.stopped:
            # Let the strategies update themselves
            for s in self.strategies:
                # See if the strategy has anything to offer
                new_order = s.refresh()
                if not new_order == None:
                    
                    # The strategy has suggested an order, so attempt to place the order.
                    self.log.write('in daemon.start(): entering trade')
                    order_result = self.oanda_instance.place_order( new_order )
                    order_result_str = json.loads(order_result) #TODO put json.loads inside place_order()

                    # TODO Check if the order failed, call the strategy's callback function 
                    # TODO Check if market closed here
                    order_rejected = False
                    if order_rejected:
                        self.log.write('daemon.py: daemon.start(): Order rejected.')
                        continue

                    # TODO what if I forget to call callback here? Need to ensure it is called, and some failsafe.
                    # So I add the order id to the order object that was passed in. Fine as long as objects are 
                    # passed by reference....
                    new_order.transaction_id = order_result_str['tradeOpened']['id']
                    s.callback( new_order )

                else:
                    # Strategy has nothing to offer at the moment.
                    self.log.write('daemon.py: daemon.start(): Strategy "', str(s), '" placed no new orders.')
            
            # limit API request frequency
            self.log.write('daemon.py: start(): Sleeping.')
            time.sleep(1)

    def stop(self):
        self.stopped = True


if __name__ == "__main__":
    d = daemon()
    d.start()


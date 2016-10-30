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
import log
import fifty
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
        log.clear_log()
        log.write_to_log( datetime.datetime.now().strftime("%c") + "\n\n" )
        self.oanda_instance = oanda.oanda()

        # strategies to run
        self.strategies = []
        self.strategies.append( fifty.fifty() )


    def start(self):
        self.stopped = False
        if self.oanda_instance.practice:
            log.write_to_log('Using practice mode.')
        else:
            log.write_to_log('Using live account.')

        # Loop:
        #   
        while not self.stopped:
            if True: #TODO: check if market is open

                # Let the strategies update themselves
                for s in self.strategies:
                    new_opp_info = s.refresh()
                    if not new_opp_info == None:
                        # Place the order 
                        log.write_to_log('in daemon.start(): entering trade')
                        order_result = oanda.place_order( new_opp_info['opp'] )
                        # TODO what if I forget to call callback here? Need to ensure it is called, and some failsafe.
                        order_result_str = json.loads(order_result)
                        order_id = order_result_str['tradeOpened']
                        s.callback_open(order_id)
                        
            # check for closed orders   
            # TODO

            # limit API request frequency
            time.sleep(1)

    def stop(self):
        self.stopped = True


if __name__ == "__main__":
    d = daemon()
    d.start()


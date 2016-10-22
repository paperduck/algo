#!/usr/bin/python3
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
import entrance
#--------------------------

class daemon():
    _orders = [] # list of open orders
    _stop = False   # flag to stop running    

    def start(self):
        oanda.clear_log()
        oanda.write_to_log( datetime.datetime.now().strftime("%c") + "\n\n" )
        if oanda.PRACTICE: #TODO: make getter/setter
            oanda.write_to_log('Using practice mode.')
        else:
            oanda.write_to_log('Using live account.')

        # Start the Entrance Scanner
        # TODO

        while True:
            if True: #TODO: check if market is open
                num_of_positions = oanda.get_num_of_positions(oanda.get_account_id_primary())
                if num_of_positions == 0:
                    # Enter a position
                    spread = round(oanda.get_spread('USD_JPY'),2)
                    oanda.write_to_log('Spread: ', spread)
                    if spread < 3:
                        # buy
                        cur_ask = round(oanda.get_ask('USD_JPY'),2)
                        sl = cur_ask - 0.05
                        tp = cur_ask + 0.10
                        oanda.write_to_log('Placing order...')
                        order_json = oanda.place_order('USD_JPY', 100, 'buy', 'market',\
                        None, None, None, None, sl, tp)
                        oanda.write_to_log ('Order response: ', order_json)
            # A little delay
            time.sleep(1)
            self.stop()
            if self._stop:
                break        

    def stop(self):
        self._stop = True


if __name__ == "__main__":
    d = daemon()
    d.start()


#!/usr/bin/python3

# File:         
# Python ver.   3.4
# Description:  Backtesting entry point.
# How to Use
#   Include the strategy module you want to test
#   Edit the line where the strategy is appended to the list of strategies
#   Run this script


import configparser
import datetime
import mysql.connector
import sys

from oanda import oanda
import fifty
import candle
from log import log

class daemon():

    def __init__(self, start=None, stop=None): # start/stop are simulation times
        self.stopped = False
        # log
        log.clear()
        log.write( datetime.datetime.now().strftime("%c") + '\n\n' )
        # set simulation start/stop times
        if start == None:
            self.start_datetime = datetime.datetime(year=2002, month=10, day=21, hour=2, minute=1)
        else:
            self.start_datetime = start
        if stop == None:
            self.stop_datetime = datetime.datetime(year=2014, month=10, day=24, hour=16, minute=59)
        else:
            self.stop_datetime = stop
        # config file settings
        self.cfg = configparser.ConfigParser()
        self.cfg.read('/home/user/raid/documents/algo.cfg')
        self.db_conn = None
        #try:
        self.db_conn = mysql.connector.connect(\
            user=self.cfg['mysql']['username'], password=self.cfg['mysql']['password'],\
            host=self.cfg['mysql']['host'], database=self.cfg['mysql']['database'])
        #except:
        #    log.write('"daemon.py" backtest.__init__(): ERROR:', sys.exc_info()[0])
        #    sys.exit()
        # initialize strategy
        self.strategies = []
        self.strategies.append( fifty.fifty( [] ) )

    def __del__(self):
        #self.db_conn.close()
        pass

    def __str__(self):
        return '[backtest class]'

    def start(self):
        # Iterate through historic candles and let the strategy do its thing.
        current_candle = oanda.get_next_candle()
        while current_candle.date < self.stop_datetime:
            for s in self.strategies:
                new_order = s.refresh()
                if new_order == None:
                    pass
                else:
                    order_result = oanda.place_order( new_order )
                    if order_result == None:
                        s.callback( False, new_order )
                    else:
                        trade = order_result['trade_opened']
                        new_order.transaction_id = trade['id']
                        s.callback( True, new_order )
            current_candle = self.get_next_candle()

        # exit all positions

        # analyze and/or save results


    def stop(self):
        self.stopped = True

if __name__ == '__main__':
    b = daemon()
    b.start()





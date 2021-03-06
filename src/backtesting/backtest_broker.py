"""
Broker simulator for backtesting strategies.
Don't use this directly. Use run_broker.py.
"""
# local imports
import csv
from datetime import datetime
import pandas as pd

# external imports
import backtesting.csv_parse as csv_parse
from log import Log
import multiprocessing as mp

class BacktestBroker():

    """ CSV files
    {    instrument_id:{
            'filename'  : string            - path to file 
            'data'      : DataFrame         - data from file
    }, ...}
    """
    files = {}

    """ {instr_id:{'buffer':<named tuple>,'active':<named tuple>},...} """
    prices = {}

    next_trade_id = 0
    initialized = False
    time = None # simulated time (time of current candle)

    @classmethod
    def init(cls, start, end, files, gap=None):
        """ Unlike the normal broker module, this one needs to be initialized manually.

        start   - datetime - start of test
        end     - datetime - end of test
        files   - {instrument_id:str, ...} - CSV files to open
        gap     - gap tolerance; timespan OK to skip when gap occurs between candles
        """
        if cls.initialized: raise Exception
        if len(files) < 1:
            print('BacktestBroker: Must add at least one file.')
            raise Exception
        else:
            for instr_id in files:
                cls.files[instr_id] = {'filename':files[instr_id]}
                cls.prices[instr_id] = {}

        cls.start_ms   = start.timestamp()
        cls.end_ms     = end.timestamp()

        """ Trades open on this simulated broker.
        trade_id:       numeric     id
        open_time:      datetime    timestamp
        instrument_id:  int         id from database
        execution_price: float      execution price
        units:          int         positive=long, negative=short
        tp:             float       take profit
        sl:             float       stop loss price
        """
        cls.trades_open = []

        """ Trade history for this simulated broker.
        trade_id:           numeric
        open_time:          datetime
        close_time:         datetime
        instrument_id:      string
        units:              number      pos=long neg=short
        execution_price:    float
        close_price:        float
        """
        cls.trades_closed = []

        with mp.Pool(mp.cpu_count()) as pool:
            for instr_id in cls.files:
                # initialize files
                f = cls.files[instr_id] # just easier to read
                # Read in the files concurrently
                f['data'] = pool.apply_async(func=csv_parse.pi, args=[ f['filename'], start, end])
            for instr_id in cls.files:
                f = cls.files[instr_id] # just easier to read
                # Wait for files to finish reading, then get a generator
                f['data'] = f['data'].get().iterrows()
                # initialize price buffer
                price = cls.prices[instr_id] # with
                price['active'] = next(f['data'])[1]    # first row
                price['buffer'] = next(f['data'])[1]    # second row
        
    @classmethod
    def advance(cls):
        """ Move one step forward.
        Return False when end of rows reached, True otherwise.
        """
        # Find oldest buffered instrument and make it active.
        oldest = None # instr_id with oldest timestamp
        for instr_id in cls.prices:
            if not oldest or cls.prices[instr_id]['buffer']['t'] < cls.prices[oldest]['buffer']['t']:
                oldest = instr_id
        cls.prices[oldest]['active'] = cls.prices[oldest]['buffer']
        """# show status
        msg = ''
        for instr_id in cls.prices:
            msg = msg + '{} {}  '.format(instr_id, cls.prices[oldest]['active']['t'].to_pydatetime())
        print(msg, end='\r')"""
        try:
            # get next row
            cls.prices[oldest]['buffer'] = next(cls.files[oldest]['data'])[1]
            cls.time = cls.prices[oldest]['buffer']['t']
        except StopIteration:
            # EOF - print summary of results
            #profits = [ t['close_price'] - t['execution_price'] for t in cls.trades_closed]
            profits = []
            for t in cls.trades_closed:
                if t['units'] > 0:
                    profits.append( t['close_price'] - t['execution_price'] )
                else:
                    profits.append( t['execution_price'] - t['close_price'] )
            profit = sum(profits)
            import numpy as np
            from scipy import stats
            wins            = [ p for p in profits if p > 0 ]
            wins_avg        = round(sum(wins)/float(len(wins)), 5) if len(wins) > 0 else 0
            wins_median     = round(np.median(wins), 5) if len(wins) > 0 else 0
            wins_mode       = stats.mode(wins) if len(wins) > 0 else 0
            wins_mode_val   = round(wins_mode[0][0], 5)
            wins_mode_count = wins_mode[1][0]
            losses              = [ p for p in profits if p < 0 ]
            losses_avg          = round(sum(losses)/float(len(losses)), 5) if len(losses) > 0 else 0
            losses_median       = round(np.median(losses), 5) if len(losses) > 0 else 0
            losses_mode         = stats.mode(losses) if len(losses) > 0 else 0
            losses_mode_val     = round(losses_mode[0][0], 5)
            losses_mode_count   = losses_mode[1][0]
            washes = [ p for p in profits if p == 0 ]
            print('\n')
            print('{} open trades'.format(len(cls.trades_open)))
            print('{} closed trades'.format(len(cls.trades_closed)))
            #print('Profits: {}'.format(profits) )
            print('Wins: {}'.format( len(wins) ))
            print('    avg:    {}'.format( wins_avg ))
            print('    median: {}'.format( wins_median ))
            print('    mode:   {} x{}'.format( wins_mode_val, wins_mode_count ))
            print('Losses: {}'.format( len(losses) ))
            print('    avg:    {}'.format( losses_avg ))
            print('    median: {}'.format( losses_median ))
            print('    mode:   {} x{}'.format( losses_mode_val, losses_mode_count ))
            print('{} Washes'.format(len(washes)))
            print('End Profit: {}'.format(profit) )
            #import pdb; pdb.set_trace()
            return False

        # Update trade statuses
        cls.trades_open = [t for t in cls.trades_open if not cls.update_closed_trade(t)]

        return True


    @classmethod
    def update_closed_trade(cls, trade):
        """ If the trade closed, mark it as such.
        Returns true if the trade closed, false if still open.
        """
        iid = trade['instrument_id']

        if (  # long SL
            trade['sl'] and trade['units'] > 0 and trade['sl'] >= cls.prices[iid]['active']['lb']
        ) or (  # short SL
            trade['sl'] and trade['units'] < 0 and trade['sl'] <= cls.prices[iid]['active']['ha']
        ):
            #print('SL HIT: execution({}) close({})'.format(trade['execution_price'], trade['sl']))
            cls.trades_closed.append( {
                'trade_id':         trade['trade_id'],
                'open_time':        trade['open_time'],
                'close_time':       cls.prices[iid]['active']['t'],
                'instrument_id':    iid,
                'units':            trade['units'],
                'execution_price':  trade['execution_price'],
                'close_price':      trade['sl']
            } )
            return True
        elif (    # long TP
            trade['tp'] and trade['units'] > 0 and trade['tp'] <= cls.prices[iid]['active']['hb']
        ) or (  # short TP
            trade['tp'] and trade['units'] < 0 and trade['tp'] >= cls.prices[iid]['active']['la']
        ):
            #print('TP HIT: execution({}) close({})'.format(trade['execution_price'], trade['tp']))
            # trade closed; add to list
            cls.trades_closed.append( {
                'trade_id':         trade['trade_id'],
                'open_time':        trade['open_time'],
                'close_time':       cls.prices[iid]['active']['t'],
                'instrument_id':    iid,
                'units':            trade['units'],
                'execution_price':  trade['execution_price'],
                'close_price':      trade['tp']
            } )
            return True

        return False


    #################################################################
    #################################################################
    # Methods to simulate a broker wrapper
    #################################################################
    #################################################################

    @classmethod
    def get_time(cls):
        """ Normally you would just call utcnow() or something """
        return cls.time

    @classmethod
    def get_bid(cls, instrument_id):
        return cls.prices[instrument_id]['active']['lb']


    @classmethod
    def get_ask(cls, instrument_id):
        return cls.prices[instrument_id]['active']['ha']


    @classmethod
    def get_spread(cls, instrument_id):
        #print('spread: {}'.format(cls.get_ask(instrument_id) - cls.get_bid(instrument_id)))
        return cls.get_ask(instrument_id) - cls.get_bid(instrument_id)
        

    @classmethod
    def get_price(cls, instrument_id):
        return (cls.get_ask(instrument_id) + cls.get_bid(instrument_id)) / 2

 
    @classmethod
    def get_volume(cls, instrument_id):
        return int(cls.prices[instrument_id]['active']['v'])


    @classmethod
    def place_trade(cls, order, units):
        """ Return trade id on success, None otherwise
        order       <Order>
        units       int
        """
        print('placing trade: {} units of {} on {}'.format(units, order.instrument.get_name(), cls.get_time()))
        iid = order.instrument.get_id()
        sl = order.stop_loss
        tp = order.take_profit
        if units == 0 or (sl==None and tp==None): raise Exception
        if units > 0: # long -> execute at ask price
            execution_price = cls.prices[iid]['active']['ha']
        else: # short -> execute at bid price
            execution_price = cls.prices[iid]['active']['lb']
        cls.trades_open.append( {
            'trade_id':         cls.next_trade_id,
            'open_time':        cls.prices[iid]['active']['t'],
            'instrument_id':    iid,
            'execution_price':  execution_price, # ignoring order.price
            'units':            units,
            'tp':               tp,
            'sl':               sl
        } )
        cls.next_trade_id += 1
        return cls.next_trade_id - 1 
        

    @classmethod
    def is_closed(cls, trade_id):
        """ """
        for t in cls.trades_closed:
            if t['trade_id'] == trade_id: return True
        return False



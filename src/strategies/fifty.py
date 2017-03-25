"""
File:               fifty.py
Python version:     3.4
Module Description: "50/50 Chance" strategy module.
Strategy Overview:
    The chances of the price going up or down are, on average, 50/50.

"""


#*************************************
import sys # sys.exit()                        
#*************************************
from broker import *
from log import Log
from opportunity import *
from order import *
from strategy import *
from trade import *
#*************************************

class Fifty(Strategy):
    """
    Class methods are used because the daemon never needs more than one
    instance of each strategy.
    """

    @classmethod
    def __init__(cls):
        """
        """
        cls.direction = 'buy'
        cls.name = "fifty"
        """
        If this class has an __init__() function, then the `open_trades`
        list defined in the base <Strategy> class cannot be used and needs
        to be defined here.
        A list of IDs is used instead of an instance of <Trades>. Might change
        in the future.
        """
        cls.open_trades = [] # list of trade IDs ("transaction ID" for Oanda)


    @classmethod
    def __str__(cls):
        """
        """
        return '50/50'


    @classmethod
    def _babysit(cls):
        """
        If there is an open trade, then babysit it. Also check if it has closed.
        "Babysit" means adjust SL, TP, expiry, units, etc.
        """
        for t in cls.open_trades:
            trade_info = Broker.get_trade( t.transaction_id )
            if trade_info == None:
                if broker.is_trade_closed( t.transaction_id ):
                    Log.write('"fifty.py" in _babysit(): Trade has closed.')
                    cls.open_trades.remove(t.transaction_id)
                else:
                    Log.write('"fifty.py" in _babysit(): broker.is_trade_closed\
                        failed for trade w/ID {}).'
                        .format(str(t.transaction_id)))
                    sys.exit()
            else:
                instrument = trade_info['instrument']
                tp = round( trade_info['takeProfit'], 2 )
                sl = round( trade_info['stopLoss'], 2 )
                side = trade_info['side']
                if side == 'buy': # BUY
                    cur_bid = Broker.get_bid( instrument )
                    if cur_bid != None:
                        if tp - cur_bid < 0.02:
                                #,str(t.transaction_id), '...')
                            new_sl = cur_bid - 0.02
                            new_tp = tp + 0.05
                            # send modify trade request
                            resp = Broker.modify_trade(t.transaction_id, new_sl, new_tp, 0)
                            if resp == None:
                                if broker.is_trade_closed( t.transaction_id ):
                                    Log.write('"fifty.py" in _babysit(): BUY trade has closed.')
                                    cls.open_trades.remove(t.transaction_id)
                                else:
                                    Log.write('"fifty.py" in _babysit(): Failed to modify BUY trade.')
                                    sys.exit() 
                            else:                                       
                                Log.write('"fifty.py" _babysit(): Modified BUY trade with ID (',\
                                     t.transaction_id, ').')
                        else:
                            pass # trade fine where it is
                    else:
                        Log.write('"fifty.py" _babysit(): Failed to get bid while babysitting.')
                        sys.exit()
                else: # SELL
                    cur_ask = Broker.get_ask( instrument )
                    if cur_ask != None:
                        if cur_ask - tp < 0.02:
                            new_sl = cur_ask + 0.02
                            new_tp = tp - 0.05
                            # send modify trade request
                            resp = Broker.modify_trade( t.transaction_id, new_sl, new_tp, 0)
                            if resp == None:
                                if broker.is_trade_closed( t.transaction_id ):
                                    Log.write('"fifty.py" in _babysit(): SELL trade has closed.')
                                    cls.open_trades.remove(t.transaction_id)
                                else:
                                    Log.write('"fifty.py" in _babysit(): Failed to modify SELL trade.')
                                    sys.exit()
                            else:
                                Log.write('"fifty.py" _babysit(): Modified SELL trade with ID (',\
                                     t.transaction_id, ').')
                        else:
                            pass # trade fine where it is
                    else:
                        Log.write('"fifty.py" _babysit(): Failed to get ask while babysitting.')
                        sys.exit()


    @classmethod
    def _scan(cls):
        """
        Look for opportunities to enter a trade.
        Returns: `opportunity` instance, or None
        """
        # switch direction
        if cls.direction == 'buy':
            cls.direction = 'sell'
        else:
            cls.direction = 'buy'
        instrument = 'USD_JPY'
        spreads = Broker.get_spreads(instrument)
        if spreads == None:
            Log.write('"fifty.py" in _scan(): Failed to get spread of {}.'
                .format(instrument)) 
            return None
        elif len(spreads) != 1:
            Log.write('"fifty.py" in _scan(): len(spreads) == {}.'
                .format(len(spreads))) 
            return None
        elif spreads[0]['status'] == 'halted':
                Log.write('"fifty.py" in _scan(): Instrument {} is halted.'
                    .format(instrument)) 
                return None
        else:
            spread = spreads[0]['spread']
            if spread < 3:
                if cls.direction == 'buy':
                    Log.write('"fifty.py" _scan(): Buying.') 
                    cur_ask_raw = Broker.get_ask('USD_JPY')
                    if cur_ask_raw != None:
                        cur_ask = round(cur_ask_raw, 2)
                        sl = cur_ask - 0.1
                        tp = cur_ask + 0.1
                    else:
                        Log.write('"fifty.py" in _scan(): Failed to get bid.')
                        sys.exit()
                        return None 
                else: # sell
                    Log.write('"fifty.py" _scan(): Selling.') 
                    cls.direction = 'sell'
                    cur_bid = Broker.get_bid('USD_JPY')
                    if cur_bid != None:
                        # Rounding the raw bid didn't prevent float inaccuracy
                        # cur_bid = round(cur_bid_raw, 2)
                        sl = round(cur_bid + 0.1, 2)
                        tp = round(cur_bid - 0.1, 2)
                    else:
                        Log.write('"fifty.py" in _scan(): Failed to get ask.') 
                        sys.exit()
                # Prepare the order and sent it back to daemon.
                opp = Opportunity()
                opp.strategy = cls.name
                # Include callback functions that point to this strategy.
                opp.trade_opened_callback = cls.trade_opened
                opp.trade_closed_callback = cls.trade_closed
                opp.confidence = 50
                opp.order = Order(
                    instrument='USD_JPY',
                    units='100',
                    side=cls.direction,
                    order_type='market',
                    stop_loss=sl,
                    take_profit=tp
                )
                Log.write('"fifty.py" _scan(): Returning opportunity with order:\n\
                    instrument: {}\n\
                    units: {}\n\
                    side: {}\n\
                    order_type: {}\n\
                    stop_loss: {}\n\
                    take_profit: {}\n'
                    .format(
                        opp.order.instrument,
                        opp.order.units,
                        opp.order.side,
                        opp.order.order_type,
                        opp.order.stop_loss,
                        opp.order.take_profit
                    )
                ) 
                return ( opp )
            else:
                return None





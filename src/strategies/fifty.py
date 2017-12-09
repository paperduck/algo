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
from broker import Broker
from instrument import Instrument
from log import Log
from opportunity import Opportunity, Opportunities
from order import Order
from strategy import Strategy
from trade import Trade, Trades
#*************************************

class Fifty(Strategy):
    """
    Class methods are used because the daemon never needs more than one
    instance of each strategy.
    """

    #Long or short? (Oanda wants 'buy' or 'sell')
    #direction = 'buy'
    go_long = True
    tp_price_diff = 0.1
    sl_price_diff = 0.1


    @classmethod
    def get_name(cls):
        """
        Return the name of the strategy.
        """
        return "Fifty"


    @classmethod
    def __str__(cls):
        """
        """
        return cls.get_name()


    @classmethod
    def _babysit(cls):
        """
        If there is an open trade, then babysit it. Also check if it has
        closed
        """
        for open_trade_id in cls._open_trade_ids:
            trade = Broker.get_trade(open_trade_id)
            if trade == None:
                Log.write('"fifty.py" _babysit(): Failed to get trade info. Checking if closed.')
                closed = Broker.is_trade_closed(open_trade_id)
                if closed[0]:
                    # If SL hit, reverse direction.
                    Log.write('\n\nLONG reason check: {} ?= {}'.format(closed[1], TradeClosedReason.sl))
                    if closed[1] == TradeClosedReason.sl:
                        if cls.go_long:
                            cls.go_long = False
                        else:
                            cls.go_long = True
                    Log.write('"fifty.py" _babysit(): Trade has closed.')
                    cls._open_trade_ids.remove(open_trade_id)
            else:
                instrument = trade.get_instrument()
                #tp = round( trade.take_profit, 2 )
                sl = round( trade.get_stop_loss(), 2 )
                go_long = trade.get_go_long()

                if go_long == True: # currently long
                    cur_bid = Broker.get_bid(instrument)
                    if cur_bid != None:
                        if cur_bid - sl > cls.sl_price_diff:
                            new_sl = cur_bid - cls.sl_price_diff
                            Log.write('modify: trade_id={}, stop_loss={}'.format(open_trade_id, new_sl))
                            resp = Broker.modify_trade(trade_id=open_trade_id, stop_loss=new_sl)
                            if resp == None:
                                Log.write('"fifty.py" _babysit(): Modify failed. Checking if trade is closed.')
                                closed = Broker.is_trade_closed(open_trade_id)
                                if closed[0]:
                                    Log.write('"fifty.py" _babysit(): BUY trade has closed. (BUY)')
                                    cls._open_trade_ids.remove(open_trade_id)
                                    # If SL hit, reverse direction.
                                    Log.write('\n\nLONG reason check: {} ?= {}'.format(closed[1], TradeClosedReason.sl))
                                    if closed[1] == TradeClosedReason.sl:
                                        cls.go_long = False
                                else:
                                    Log.write('"fifty.py" _babysit(): Failed',
                                        ' to modify BUY trade.')
                                    raise Exception
                            else:                                       
                                Log.write('"fifty.py" _babysit(): Modified BUY trade with ID (',\
                                     open_trade_id, ').')
                    else:
                        Log.write('"fifty.py" _babysit(): Failed to get bid while babysitting.')
                        raise Exception
                else: # currently short
                    cur_bid = Broker.get_bid(instrument)
                    if cur_bid != None:
                        if sl - cur_bid > cls.sl_price_diff:
                            new_sl = cur_bid + cls.sl_price_diff
                            resp = Broker.modify_trade(trade_id=open_trade_id, stop_loss=new_sl)
                            if resp == None:
                                Log.write('"fifty.py" _babysit(): Modify failed. Checking if trade is closed. (SELL)')
                                closed = Broker.is_trade_closed(open_trade_id)
                                if closed[0]:
                                    Log.write('"fifty.py" in _babysit(): SELL trade has closed.')
                                    Log.write('\n\nSHORT reason check: {} ?= {}'.format(closed[1], TradeClosedReason.sl))
                                    cls._open_trade_ids.remove(open_trade_id)
                                    # If SL hit, reverse direction.
                                    if closed[1] == TradeClosedReason.sl:
                                        cls.go_long = True
                                else:
                                    Log.write('"fifty.py" in _babysit(): Failed to modify SELL trade.')
                                    sys.exit()
                            else:
                                Log.write('"fifty.py" _babysit(): Modified SELL trade with ID (',\
                                    open_trade_id, ').')
                    else:
                        Log.write('"fifty.py" _babysit(): Failed to get ask while babysitting.')
                        sys.exit()


    @classmethod
    def _scan(cls):
        """
        Look for opportunities to enter a trade.
        Returns:
            <opportunity> object(s) if there is an opportunity
            Empty list if no opportunities.
            None on failure
        """
        # If we're babysitting a trade, don't open a new one.
        if len(cls._open_trade_ids) > 0:
            return []
        instrument = Instrument(Instrument.get_id_from_name('USD_JPY'))
        spreads = Broker.get_spreads(instrument)
        if spreads == None:
            Log.write('"fifty.py" in _scan(): Failed to get spread of {}.'
                .format(instrument.get_name())) 
            return []
        elif len(spreads) < 1:
            Log.write('"fifty.py" in _scan(): len(spreads) == {}.'
                .format(len(spreads))) 
            return None
        # This only checks for one instrument.
        elif spreads[0]['status'] == 'halted':
                Log.write('"fifty.py" in _scan(): Instrument {} is halted.'
                    .format(instrument.get_name())) 
                return []
        else:
            spread = spreads[0]['spread']
            if spread < 3:
                if cls.go_long: # buy
                    Log.write('"fifty.py" _scan(): Going long.') 
                    cur_bid = Broker.get_bid(instrument)
                    if cur_bid != None:
                        # Rounding the raw bid didn't prevent float inaccuracy
                        # cur_bid = round(cur_bid_raw, 2)
                        tp = round(cur_bid + cls.tp_price_diff, 2)
                        sl = round(cur_bid - cls.sl_price_diff, 2)
                    else:
                        Log.write('"fifty.py" in _scan(): Failed to get bid.')
                        sys.exit()
                        return None 
                else: # sell
                    Log.write('"fifty.py" _scan(): Shorting.') 
                    cls.go_long = False
                    cur_bid = Broker.get_bid(instrument)
                    if cur_bid != None:
                        tp = round(cur_bid - cls.tp_price_diff, 2)
                        sl = round(cur_bid + cls.sl_price_diff, 2)
                    else:
                        Log.write('"fifty.py" in _scan(): Failed to get ask.') 
                        sys.exit()
                # Prepare the order and sent it back to daemon.
                opp = Opportunity()
                opp.strategy = cls
                opp.confidence = 50
                opp.order = Order(
                    instrument=instrument,
                    order_type='market',
                    go_long=cls.go_long,
                    stop_loss=sl,
                    take_profit=tp,
                    units='100'
                )
                Log.write('"fifty.py" _scan(): Returning opportunity with \
                    order:\n{}'.format(opp))
                return ( opp )
            else:
                return []





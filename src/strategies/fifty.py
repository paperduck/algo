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

    #Long or short? (Oanda specifically takes 'buy' or 'sell' as argument)
    #direction = 'buy'
    go_long = True


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
        closed. "Babysit" means adjust SL, TP, expiry, units, etc.
        """
        for trade_id in cls._open_trades:
            trade = Broker.get_trade(trade_id)
            if trade == None:
                Log.write('"fifty.py" _babysit(): Failed to get trade info. Checking if closed.')
                if Broker.is_trade_closed(trade_id)[0]:
                    Log.write('"fifty.py" _babysit(): Trade has closed.')
                    cls._open_trades.remove(trade_id)
            else:
                instrument = trade.instrument
                tp = round( trade.take_profit, 2 )
                sl = round( trade.stop_loss, 2 )
                side = trade.side
                if side == 'buy': # currently long
                    cur_bid = Broker.get_bid( instrument )
                    if cur_bid != None:
                        if tp - cur_bid < 0.02:
                            new_sl = cur_bid - 0.02
                            # new_tp = tp + 0.05
                            # send modify trade request
                            resp = Broker.modify_trade(trade_id, new_sl, new_tp, 0)
                            if resp == None:
                                Log.write('"fifty.py" _babysit(): Modify failed. Checking if trade is closed.')
                                closed = Broker.is_trade_closed(trade_id)
                                if closed[0]:
                                    Log.write('"fifty.py" _babysit(): BUY trade has closed. (BUY)')
                                    cls._open_trades.remove(trade_id)
                                    # check reason
                                    if closed[1] == TradeClosedReason.sl:
                                        cls.go_long = False
                                else:
                                    Log.write('"fifty.py" _babysit(): Failed',
                                        ' to modify BUY trade.')
                                    raise Exception
                            else:                                       
                                Log.write('"fifty.py" _babysit(): Modified BUY trade with ID (',\
                                     trade_id, ').')
                        else:
                            pass # trade fine where it is
                    else:
                        Log.write('"fifty.py" _babysit(): Failed to get bid while babysitting.')
                        sys.exit()
                else: # currently short
                    cur_ask = Broker.get_ask( instrument )
                    if cur_ask != None:
                        if cur_ask - tp < 0.02:
                            new_sl = cur_ask + 0.02
                            #new_tp = tp - 0.05
                            # send modify trade request
                            resp = Broker.modify_trade(
                                trade_id=trade_id,
                                stop_loss=new_sl,
                                take_profit=new_tp,
                                trailing_stop=0
                            )
                            if resp == None:
                                Log.write('"fifty.py" _babysit(): Modify failed. Checking if trade is closed. (SELL)')
                                closed = Broker.is_trade_closed(trade_id)
                                if closed[0]:
                                    Log.write('"fifty.py" in _babysit(): SELL trade has closed.')
                                    cls._open_trades.remove(trade_id)
                                    # check reason
                                    if closed[1] == TradeClosedReason.sl:
                                        cls.go_long = True
                                else:
                                    Log.write('"fifty.py" in _babysit(): Failed to modify SELL trade.')
                                    sys.exit()
                            else:
                                Log.write('"fifty.py" _babysit(): Modified SELL trade with ID (',\
                                    trade_id, ').')
                        else:
                            pass # trade fine where it is
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
        if len(cls._open_trades) > 0:
            return []
        instrument = 'USD_JPY'
        spreads = Broker.get_spreads(instrument)
        if spreads == None:
            Log.write('"fifty.py" in _scan(): Failed to get spread of {}.'
                .format(instrument)) 
            return []
        elif len(spreads) < 1:
            Log.write('"fifty.py" in _scan(): len(spreads) == {}.'
                .format(len(spreads))) 
            return None
        # This only checks for one instrument.
        elif spreads[0]['status'] == 'halted':
                Log.write('"fifty.py" in _scan(): Instrument {} is halted.'
                    .format(instrument)) 
                return []
        else:
            spread = spreads[0]['spread']
            if spread < 3:
                if cls.go_long: # buy
                    Log.write('"fifty.py" _scan(): Going long.') 
                    cur_ask_raw = Broker.get_ask('USD_JPY')
                    if cur_ask_raw != None:
                        #cur_ask = round(cur_ask_raw, 2)
                        sl = round(cur_ask - 0.1, 2)
                        tp = round(cur_ask + 0.1, 2)
                    else:
                        Log.write('"fifty.py" in _scan(): Failed to get bid.')
                        sys.exit()
                        return None 
                else: # sell
                    Log.write('"fifty.py" _scan(): Shorting.') 
                    cls.go_long = 'sell'
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
                opp.strategy = cls
                opp.confidence = 50
                opp.order = Order(
                    instrument='USD_JPY',
                    order_type='market',
                    side=cls.go_long,
                    stop_loss=sl,
                    take_profit=tp,
                    units='100'
                )
                Log.write('"fifty.py" _scan(): Returning opportunity with \
                    order:\n{}'.format(opp))
                return ( opp )
            else:
                return []





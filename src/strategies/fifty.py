"""
Strategy Overview: price goes up or down; 50/50 chance.
"""

from broker import Broker
from instrument import Instrument
from log import Log
from opportunity import Opportunity, Opportunities
from order import Order
from strategy import Strategy
from trade import Trade, Trades, TradeClosedReason

class Fifty(Strategy):
    #Long or short?
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
        """ (See strategy.py for documentation) """
        Log.write('fifty.py babysit(): _open_tade_ids: {}'.format(cls._open_trade_ids))

        for open_trade_id in cls._open_trade_ids:
            is_closed = Broker.is_trade_closed(open_trade_id)
            if is_closed[0]:
                Log.write('"fifty.py" _babysit(): Trade ({}) has closed with reason: {}'
                    .format( open_trade_id, str(is_closed[1]) )
                )
                # If SL hit, reverse direction.
                if is_closed[1] == TradeClosedReason.STOP_LOSS_ORDER:
                    if cls.go_long:
                        cls.go_long = False
                    else:
                        cls.go_long = True
                cls._open_trade_ids.remove(open_trade_id)
            else:
                trade = Broker.get_trade(open_trade_id)
                instrument = trade.instrument
                sl = round( float(trade.stop_loss), 2 )
                go_long = int(trade.units) > 0

                if go_long: # currently long
                    cur_bid = Broker.get_bid(instrument)
                    if cur_bid != None:
                        if cur_bid - sl > cls.sl_price_diff:
                            new_sl = cur_bid - cls.sl_price_diff
                            resp = Broker.modify_trade(
                                trade_id=open_trade_id,
                                stop_loss_price=str(round(new_sl, 2))
                            )
                            if resp == None:
                                Log.write('"fifty.py" _babysit(): Modify failed. Checking if trade is closed.')
                                closed = Broker.is_trade_closed(open_trade_id)
                                Log.write('fifty.py babysit(): is_trade_closed returned:\n{}'.format(closed))
                                if closed[0]:
                                    Log.write('"fifty.py" _babysit(): BUY trade has closed. (BUY)')
                                    cls._open_trade_ids.remove(open_trade_id)
                                    # If SL hit, reverse direction.
                                    if closed[1] == TradeClosedReason.STOP_LOSS_ORDER:
                                        cls.go_long = False
                                else:
                                    Log.write('"fifty.py" _babysit(): Failed to modify BUY trade.')
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
                            resp = Broker.modify_trade(
                                trade_id=open_trade_id, 
                                stop_loss_price=str(round(new_sl, 2))
                            )
                            if resp == None:
                                closed = Broker.is_trade_closed(open_trade_id)
                                Log.write('fifty.py babysit(): is_trade_closed returned:\n{}'.format(closed))
                                if closed[0]:
                                    Log.write('"fifty.py" _babysit(): SELL trade has closed. (BUY)')
                                    cls._open_trade_ids.remove(open_trade_id)
                                    # If SL hit, reverse direction.
                                    if closed[1] == TradeClosedReason.STOP_LOSS_ORDER:
                                        cls.go_long = True
                                else:
                                    Log.write('"fifty.py" in _babysit(): Failed to modify SELL trade.')
                                    raise Exception
                            else:
                                Log.write('"fifty.py" _babysit(): Modified SELL trade with ID (',\
                                    open_trade_id, ').')
                    else:
                        Log.write('"fifty.py" _babysit(): Failed to get ask while babysitting.')
                        raise Exception


    @classmethod
    def _scan(cls):
        Log.write('fifty.py scan()')
        """ (see strategy.py for documentation) """
        # If we're babysitting a trade, don't open a new one.
        if len(cls._open_trade_ids) > 0:
            Log.write('fifty.py _scan(): Trades open; no suggestions.')
            return []
        instrument = Instrument(Instrument.get_id_from_name('USD_JPY'))
        spreads = Broker.get_spreads([instrument])
        if spreads == None:
            Log.write('"fifty.py" in _scan(): Failed to get spread of {}.'
                .format(instrument.get_name())) 
            raise Exception
        elif len(spreads) < 1:
            Log.write('"fifty.py" in _scan(): len(spreads) == {}.'
                .format(len(spreads))) 
            raise Exception
        # This only checks for one instrument.
        elif not spreads[0]['tradeable']:
                Log.write('"fifty.py" in _scan(): Instrument {} not tradeable.'
                    .format(instrument.get_name())) 
                return []
        else:
            spread = spreads[0]['spread']
            if spread < 3:
                Log.write('fifty.py _scan(): spread = {}'.format(spread))
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
                        raise Exception
                else: # sell
                    Log.write('"fifty.py" _scan(): Shorting.') 
                    cls.go_long = False
                    cur_bid = Broker.get_bid(instrument)
                    if cur_bid != None:
                        tp = round(cur_bid - cls.tp_price_diff, 2)
                        sl = round(cur_bid + cls.sl_price_diff, 2)
                    else:
                        Log.write('"fifty.py" in _scan(): Failed to get ask.') 
                        raise Exception
                # Prepare the order and sent it back to daemon.
                units = -1
                if cls.go_long:
                    units = 1
                opp = Opportunity()
                opp.strategy = cls
                opp.confidence = 50
                opp.order = Order(
                    instrument=instrument,
                    order_type="MARKET", # matches Oanda's OrderType definition
                    stop_loss={ "price" : str(sl) },
                    take_profit={ "price" : str(tp) },
                    units=units
                )
                Log.write('"fifty.py" _scan(): Returning opportunity with \
                    order:\n{}'.format(opp))
                return [opp]
            else:
                Log.write('fifty.py _scan(): Spread is high; no suggestions.')
                return []





#!/usr/bin/python3

# fifty.py
# Fifty-fifty strategy
# Python 3.4
# Description: "50/50 Chance" strategy.


#*************************************
import sys # sys.exit()                        
#*************************************
from broker import *
from log import *
from opportunity import *
from order import *
from strategy import *
from trade import *
#*************************************

class Fifty(Strategy):

    def __init__(self):
        """
        """
        self.next_direction = 'buy'
        self.name = "fifty"
        """
        If this class has an __init__() function, then the `open_trades`
        list defined in the base Strategy class cannot be used and needs
        to be defined here.
        """
        self.open_trades = []


    def __str__(self):
        """
        """
        return '50/50'


    def check_trade_closed(self, transaction_id):
        """
        Returns: Bool or (None on failure)
        TODO: A similar function is going to be called in any strategy, so
        put this in broker.py.
        """
        # TODO If I decide to hold multiple current trades, I need to specify which 
        # order to pop. For now, just assume there is only one.
        closed = Broker.is_trade_closed( transaction_id )
        if closed == None:
            log.write('"fifty.py" in check_trade_closed(): Call to broker.is_trade_closed() failed')
            sys.exit()
        else:
            if closed:
                log.write('"fifty.py" check_trade_closed(): Trade with ID ', transaction_id, ' closed.')

                # this in particular needs
                # to go in broker.py so 
                # I don't forget to add it to each strategy.
                log.transaction( transaction_id )
            return closed


    def babysit(self):
        """
        If there is an open trade, then babysit it. Also check if it has closed.
        Otherwise, look for a new opportunity to enter a position.
        """
        if len(self.open_trades) >= 1:
            for t in self.open_trades:
                # Trade is still active; babysit open position; adjust SL, TP, expiry, units, etc.
                #    ' should be modified.')
                trade_info = Broker.get_trade( t.transaction_id )
                if trade_info == None:
                    if self.check_trade_closed( t.transaction_id ):
                        log.write('"fifty.py" in babysit(): Trade has closed.')
                    else:
                        log.write('"fifty.py" in babysit(): check_trade_closed() failed for trade w/ID '\
                             + str(t.transaction_id), ').')
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
                                    if self.check_trade_closed( t.transaction_id ):
                                        log.write('"fifty.py" in babysit(): BUY trade has closed.')
                                    else:
                                        log.write('"fifty.py" in babysit(): Failed to modify BUY trade.')
                                        sys.exit() 
                                else:                                       
                                    log.write('"fifty.py" babysit(): Modified BUY trade with ID (',\
                                         t.transaction_id, ').')
                            else:
                                pass # trade fine where it is
                        else:
                            log.write('"fifty.py" babysit(): Failed to get bid while babysitting.')
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
                                    if self.check_trade_closed( t.transaction_id ):
                                        log.write('"fifty.py" in babysit(): SELL trade has closed.')
                                    else:
                                        log.write('"fifty.py" in babysit(): Failed to modify SELL trade.')
                                        sys.exit()
                                else:
                                    log.write('"fifty.py" babysit(): Modified SELL trade with ID (',\
                                         t.transaction_id, ').')
                            else:
                                pass # trade fine where it is
                        else:
                            log.write('"fifty.py" babysit(): Failed to get ask while babysitting.')
                            sys.exit()


    def scan(self):
        """
        Look for opportunities to enter a trade.
        Returns: `opportunity` or None
        """
        spread_ = Broker.get_spread('USD_JPY')
        if spread_ == None:
            log.write('"fifty.py" in scan(): Failed to get spread.') 
            return None
        else:
            spread = round(spread_, 2)
            if spread < 3: # return this opportunity
                if self.next_direction == 'buy':
                    cur_ask_raw = Broker.get_ask('USD_JPY')
                    if cur_ask_raw != None:
                        cur_ask = round(cur_ask_raw, 2)
                        sl = cur_ask - 0.1
                        tp = cur_ask + 0.1
                    else:
                        log.write('"fifty.py" in scan(): Failed to get bid.')
                        sys.exit()
                        return None 
                else: # sell
                    self.next_direction = 'sell'
                    cur_bid_raw = Broker.get_bid('USD_JPY')
                    if cur_bid_raw != None:
                        cur_bid = round(cur_bid_raw, 2)
                        sl = cur_bid + 0.1
                        tp = cur_bid - 0.1
                    else:
                        log.write('"fifty.py" in scan(): Failed to get ask.') 
                        sys.exit()
                # switch direction for next time
                if self.next_direction == 'buy':
                    self.next_direction = 'sell'
                else:
                    self.next_direction = 'buy'
                # Prepare the order and sent it back to daemon.
                opp = Opportunity()
                opp.strategy = self.name
                opp.confidence = 50
                opp.order = Order(
                    'USD_JPY', '100', self.next_direction, 'market', None, None,
                    None, None, sl, tp, None
                )
                return ( opp )
            else:
                return None


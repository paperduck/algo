#!/usr/bin/python3

# fifty.py
# Fifty-fifty strategy
# Python 3.4
# Description: "50/50 Chance" strategy.
#   The idea is that if you blindly pick an instrument, there is a 50/50 chance it will go up or down.
#   This strategy starts with that probability then minimizes loss and lets winners ride. 

#*************************************
import sys # sys.exit()                        
#*************************************
from log import log
from oanda import oanda
import order
from strategy import strategy
import trade
#*************************************

class fifty( strategy ):

    def __init__(self, in_preexisting_trades):
        self.next_direction = 'buy'
        self.open_trades = []     # list of `trade' objects?
        self.closed_trades = []       # list of `trade' objects?
        # Fill up the list of open orders TODO
        for t in in_preexisting_trades:
            # Query db for the trade opened by this strategy.
            my_open_trades = []
            for t in my_open_trades:
                print( '"fifty.py" __init__(): pre-existing trade ID: ', t.trade_id )
                #self.open_trades.append( trade( xxx ) )

    def __str__(self):
        return '50/50'

    # Returns: Bool or (None on failure)
    # TODO: A similar function is going to be called in any strategy, so put this in oanda.py.
    def check_trade_closed(self, transaction_id):
        # TODO If I decide to hold multiple current trades, I need to specify which 
        # order to pop. For now, just assume there is only one.
        closed = oanda.is_trade_closed( transaction_id )
        if closed == None:
            log.write('"fifty.py" in check_trade_closed(): Call to oanda.is_trade_closed() failed')
            sys.exit()
        else:
            if closed:
                log.write('"fifty.py" refresh(): Trade with ID ', transaction_id, ' closed.')
                self.closed_trades.append( self.open_trades.pop() )
                log.transaction( transaction_id ) # this in particular needs to go in oanda.py so 
                # I don't forget to add it to each strategy.
            return closed
        
    # Look at current price and past prices and determine whether there is an opportunity or not.
    # Returns:
    #   If the daemon should enter a trade, an instance of `order', otherwise
    #   None.
    def refresh(self):
        #log.write('"fifty.py" refresh(): Entering function.')
        # If there is an open trade, then babysit it. Also check if it has closed.
        # Otherwise, look for a new opportunity to enter a position.
        if len(self.open_trades) >= 1:
            for t in self.open_trades:
                # Trade is still active; babysit open position; adjust SL, TP, expiry, units, etc.
                #log.write('"fifty.py" refresh(): Checking if trade with ID ', t.transaction_id,\
                #    ' should be modified.')
                trade_info = oanda.get_trade( t.transaction_id )
                if trade_info == None:
                    if self.check_trade_closed( t.transaction_id ):
                        log.write('"fifty.py" in refresh(): Trade has closed.')
                    else:
                        log.write('"fifty.py" in refresh(): check_trade_closed() failed for trade w/ID '\
                             + str(t.transaction_id), ').')
                        sys.exit()
                else:
                    instrument = trade_info['instrument']
                    tp = round( trade_info['takeProfit'], 2 )
                    sl = round( trade_info['stopLoss'], 2 )
                    side = trade_info['side']
                    if side == 'buy': # BUY
                        cur_bid = oanda.get_bid( instrument )
                        if cur_bid != None:
                            if tp - cur_bid < 0.02:
                                #log.write('"fifty.py" refresh(): Modifying BUY trade with ID: '\
                                    #,str(t.transaction_id), '...')
                                new_sl = cur_bid - 0.02
                                new_tp = tp + 0.05
                                # send modify trade request
                                resp = oanda.modify_trade(t.transaction_id, new_sl, new_tp, 0)
                                if resp == None:
                                    if self.check_trade_closed( t.transaction_id ):
                                        log.write('"fifty.py" in refresh(): BUY trade has closed.')
                                    else:
                                        log.write('"fifty.py" in refresh(): Failed to modify BUY trade.')
                                        sys.exit() 
                                else:                                       
                                    log.write('"fifty.py" refresh(): Modified BUY trade with ID (',\
                                         t.transaction_id, ').')
                            else:
                                pass # trade fine where it is
                        else:
                            log.write('"fifty.py" refresh(): Failed to get bid while babysitting.')
                            sys.exit()
                    else: # SELL
                        cur_ask = oanda.get_ask( instrument )
                        if cur_ask != None:
                            if cur_ask - tp < 0.02:
                                #log.write('"fifty.py" refresh(): Modifying SELL trade with ID ', str(t.transaction_id) )
                                new_sl = cur_ask + 0.02
                                new_tp = tp - 0.05
                                # send modify trade request
                                resp = oanda.modify_trade( t.transaction_id, new_sl, new_tp, 0)
                                if resp == None:
                                    if self.check_trade_closed( t.transaction_id ):
                                        log.write('"fifty.py" in refresh(): SELL trade has closed.')
                                    else:
                                        log.write('"fifty.py" in refresh(): Failed to modify SELL trade.')
                                        sys.exit()
                                else:
                                    log.write('"fifty.py" refresh(): Modified SELL trade with ID (',\
                                         t.transaction_id, ').')
                            else:
                                pass # trade fine where it is
                        else:
                            log.write('"fifty.py" refresh(): Failed to get ask while babysitting.')
                            sys.exit()
        else:
            # No open trades, so look for opportunities to enter a trade
            spread_ = oanda.get_spread('USD_JPY')
            if spread_ == None:
                log.write('"fifty.py" in refresh(): Failed to get spread.') 
                return None
            else:
                spread = round(spread_, 2)
                log.write('"fifty.py" in refresh(): Spread =  ', spread)
                if spread < 3: # return this opportunity
                    if self.next_direction == 'buy':
                        cur_ask_raw = oanda.get_ask('USD_JPY')
                        if cur_ask_raw != None:
                            cur_ask = round(cur_ask_raw, 2)
                            sl = cur_ask - 0.1
                            tp = cur_ask + 0.1
                        else:
                            log.write('"fifty.py" in refresh(): Failed to get bid.')
                            sys.exit()
                            return None 
                    else: # sell
                        self.next_direction = 'sell'
                        cur_bid_raw = oanda.get_bid('USD_JPY')
                        if cur_bid_raw != None:
                            cur_bid = round(cur_bid_raw, 2)
                            sl = cur_bid + 0.1
                            tp = cur_bid - 0.1
                        else:
                            log.write('"fifty.py" in refresh(): Failed to get ask.') 
                            sys.exit()
                    # Prepare the order.
                    opp = order.order('USD_JPY', '100', self.next_direction, 'market', None, None, None, None, sl, tp, None)
                    # switch direction for next time
                    if self.next_direction == 'buy':
                        self.next_direction = 'sell'
                    else:
                        self.next_direction = 'buy'
                    # send opportunity back to the main daemon.
                    return ( opp )

    # Analyze the result of a suggestion.
    # new_order is an instance of `order`.
    # `order` is a Bool of success/failure.
    def callback(self, opened, new_order):    
        if opened:
            log.write('"fifty.py" in callback(): Trade opened. ID: ', new_order.transaction_id)
            self.open_trades.append( new_order )
        else:
            log.write('"fifty.py" in callback(): Failed to open trade with Order ID: ', new_order.transaction_id,\
                '. ABORTING.')
            sys.exit()
        

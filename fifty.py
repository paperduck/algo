#!/usr/bin/python3

# fifty.py
# Fifty-fifty strategy
# Python 3.4

import oanda
import log as loggy
import order
import sys # sys.exit()                        

class fifty():

    def __init__(self):
        self.oanda_instance = oanda.oanda()
        self.next_direction = 'buy'
        self.open_trades = []     # list of `order' objects?
        self.closed_trades = []       # list of `order' objects?
        self.log = loggy.log(True)
        # Fill up the list of open orders
        # TODO

    def __str__(self):
        return '50/50'

    # Returns: Bool or (None on failure)
    def check_trade_closed(self, transaction_id):
        # TODO If I decide to hold multiple current trades, I need to specify which 
        # order to pop. For now, just assume there is only one.
        closed = self.oanda_instance.is_trade_closed( transaction_id )
        if closed == None:
            self.log.write('"fifty.py" in check_trade_closed(): Call to oanda.is_trade_closed() failed')
            sys.exit()
        else:
            if closed:
                self.log.write('"fifty.py" refresh(): Trade with ID ', transaction_id, ' closed.')
                self.closed_trades.append( self.open_trades.pop() )
                self.log.transaction( transaction_id )
            return closed
        
    # Look at current price and past prices and determine whether there is an opportunity or not.
    # Returns:
    #   If the daemon should enter a trade, an instance of `order', otherwise
    #   None.
    def refresh(self):
        #self.log.write('"fifty.py" refresh(): Entering function.')
        # If there is an open trade, then babysit it. Also check if it has closed.
        # Otherwise, look for a new opportunity to enter a position.
        if len(self.open_trades) >= 1:
            for t in self.open_trades:
                # Trade is still active; babysit open position; adjust SL, TP, expiry, units, etc.
                #self.log.write('"fifty.py" refresh(): Checking if trade with ID ', t.transaction_id,\
                #    ' should be modified.')
                trade_info = self.oanda_instance.get_trade_info( t.transaction_id )
                if trade_info == None:
                    if self.check_trade_closed( t.transaction_id ):
                        self.log.write('"fifty.py" in refresh(): Trade has closed.')
                    else:
                        self.log.write('"fifty.py" in refresh(): check_trade_closed() failed for trade w/ID '\
                             + str(t.transaction_id), ').')
                        sys.exit()
                else:
                    instrument = trade_info['instrument']
                    tp = round( trade_info['takeProfit'], 2 )
                    sl = round( trade_info['stopLoss'], 2 )
                    side = trade_info['side']
                    if side == 'buy': # BUY
                        cur_bid = self.oanda_instance.get_bid( instrument )
                        if cur_bid != None:
                            if cur_bid - sl > 0.05:
                                #self.log.write('"fifty.py" refresh(): Modifying BUY trade with ID: '\
                                    #,str(t.transaction_id), '...')
                                new_sl = cur_bid - 0.05
                                new_tp = cur_bid + 0.1
                                # send modify trade request
                                resp = self.oanda_instance.modify_trade(t.transaction_id, new_sl, new_tp, 0)
                                if resp == None:
                                    if self.check_trade_closed( t.transaction_id ):
                                        self.log.write('"fifty.py" in refresh(): BUY trade has closed.')
                                    else:
                                        self.log.write('"fifty.py" in refresh(): Failed to modify BUY trade.')
                                        sys.exit() 
                                else:                                       
                                    self.log.write('"fifty.py" refresh(): Modified BUY trade with ID (',\
                                         t.transaction_id, ').')
                            else:
                                pass # trade fine where it is
                        else:
                            self.log.write('"fifty.py" refresh(): Failed to get bid while babysitting.')
                            sys.exit()
                    else: # SELL
                        cur_ask = self.oanda_instance.get_ask( instrument )
                        if cur_ask != None:
                            if sl - cur_ask > 0.05:
                                #self.log.write('"fifty.py" refresh(): Modifying SELL trade with ID ', str(t.transaction_id) )
                                new_sl = cur_ask + 0.05
                                new_tp = cur_ask - 0.1
                                # send modify trade request
                                resp = self.oanda_instance.modify_trade( t.transaction_id, new_sl, new_tp, 0)
                                if resp == None:
                                    if self.check_trade_closed( t.transaction_id ):
                                        self.log.write('"fifty.py" in refresh(): SELL trade has closed.')
                                    else:
                                        self.log.write('"fifty.py" in refresh(): Failed to modify SELL trade.')
                                        sys.exit()
                                else:
                                    self.log.write('"fifty.py" refresh(): Modified SELL trade with ID (',\
                                         t.transaction_id, ').')
                            else:
                                pass # trade fine where it is
                        else:
                            self.log.write('"fifty.py" refresh(): Failed to get ask while babysitting.')
                            sys.exit()
        else:
            # No open trades, so look for opportunities to enter a trade
            spread_ = self.oanda_instance.get_spread('USD_JPY')
            if spread_ == None:
                self.log.write('"fifty.py" in refresh(): Failed to get spread.') 
                return None
            else:
                spread = round(spread_, 2)
                self.log.write('"fifty.py" in refresh(): Spread =  ', spread)
                if spread < 3: # return this opportunity
                    if self.next_direction == 'buy':
                        cur_bid_raw = self.oanda_instance.get_bid('USD_JPY')
                        if cur_bid_raw != None:
                            cur_bid = round(cur_bid_raw, 2)
                            sl = cur_bid - 0.05
                            tp = cur_bid + 0.1
                        else:
                            self.log.write('"fifty.py" in refresh(): Failed to get bid.')
                            sys.exit()
                            return None 
                    else: # sell
                        self.next_direction = 'sell'
                        cur_ask_raw = self.oanda_instance.get_ask('USD_JPY')
                        if cur_ask_raw != None:
                            cur_ask = round(cur_ask_raw, 2)
                            sl = cur_ask + 0.05
                            tp = cur_ask - 0.1
                        else:
                            self.log.write('"fifty.py" in refresh(): Failed to get ask.') 
                            sys.exit()
                            return None
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
            self.log.write('"fifty.py" in callback(): Trade opened. ID: ', new_order.transaction_id)
            self.open_trades.append( new_order )
        else:
            self.log.write('"fifty.py" in callback(): Trade failed to open. ID: ', new_order.transaction_id)
        

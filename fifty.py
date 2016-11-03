# fifty.py
# Fifty-fifty strategy
# Python 3.4

import oanda
import log as loggy
import order

class fifty():

    def __init__(self):
        self.oanda_instance = oanda.oanda()
        self.next_direction = 'buy'
        self.current_trades = []     # list of `order' objects?
        self.past_trades = []       # list of `order' objects?
        self.log = loggy.log(True)
        # Fill up the list of open orders
        # TODO

    def __str__(self):
        return '50/50'

    # Look at current price and past prices and determine whether there is an opportunity or not.
    # Returns:
    #   If the daemon should enter a trade, an instance of `order', otherwise
    #   None.
    def refresh(self):
        self.log.write('"fifty.py" refresh(): Entering function.')
        # If there is an open trade, then babysit it. Also check if it has closed.
        # Otherwise, look for a new opportunity to enter a position.
        if len(self.current_trades) >= 1:
            # First, check if trade is closed
            for t in self.current_trades:
                if self.oanda_instance.is_trade_closed( t.transaction_id ):
                    # TODO If I decide to hold multiple current trades, I need to specify which 
                    # order to pop. For now, just assume there is only one.
                    self.log.write('"fity.py" refresh(): Trade with ID ', t.transaction_id, ' closed.')
                    self.past_trades.append( self.current_trade.pop() )
                else:                    
                    # Trade is still active; babysit open position: adjust SL, TP, expiry, units, etc.
                    self.log.write('"fifty.py" refresh(): Checking if trade with ID ', t.transaction_id,\
                        ' should be modified.')
                    trade_info = self.oanda_instance.get_trade_info( t.transaction_id )
                    if trade_info == None:
                        self.log.write(\
                            '"fifty.py" in refresh(): Failed to get trade info for trade ' + str(t.transaction_id)
                        )
                        self.log.write('"fifty.py" refresh(): Exiting program.')
                        sys.exit()
                    instrument = trade_info['instrument']
                    tp = round( trade_info['takeProfit'], 2 )
                    sl = round( trade_info['stopLoss'], 2 )
                    side = trade_info['side']
                    self.log.write('"fifty.py" refresh(): current trade has side = ', side)
                    if side == 'buy': # try to move sl and tp up
                        cur_bid = self.oanda_instance.get_bid( instrument )
                        if cur_bid - sl > 0.05:
                            self.log.write('"fifty.py" refresh(): Modifying BUY trade with ID ', str(t.transaction_id) )
                            new_sl = cur_bid - 0.05
                            new_tp = cur_bid + 0.1
                            # send modify trade request
                            resp = self.oanda_instance.modify_trade( t.transaction_id, new_sl, new_tp, 0)
                            self.log.write('"fifty.py" refresh(): Trade (', t.transaction_id, ') modified.')
                            return None
                    else: # try to move sl and tp down
                        cur_ask = self.oanda_instance.get_ask( instrument )
                        if sl - cur_ask > 0.05:
                            self.log.write('"fifty.py" refresh(): Modifying SELL trade with ID ', str(t.transaction_id) )
                            new_sl = cur_ask + 0.05
                            new_tp = cur_bid - 0.1
                            # send
                            resp = self.oanda_instance.modify_trade( t.transaction_id, new_sl, new_tp, 0)
                            self.log.write('"fifty.py" refresh(): Trade (', t.transaction_id, ') modified.')
                        return None
        else:
            # No open trades, so look for opportunities to enter a trade
            spread = round(self.oanda_instance.get_spread('USD_JPY'),2)
            self.log.write('fifty.py: refresh(): Spread =  ', spread)
            if spread < 3:
                # return opportunity
                if self.next_direction == 'buy':
                    cur_bid = round(self.oanda_instance.get_bid('USD_JPY') ,2)
                    sl = cur_bid - 0.05
                    tp = cur_bid + 0.1
                else:
                    # sell
                    self.next_direction = 'sell'
                    cur_ask = round(self.oanda_instance.get_ask('USD_JPY') ,2)
                    sl = cur_ask + 0.05
                    tp = cur_ask - 0.1

                # Prepare new opportunity. Everything that will be passed to the REST API is a string.
                opp = order.order('USD_JPY', '100', self.next_direction, 'market', None, None, None, None, sl, tp, None)
                # switch direction for next time
                if self.next_direction == 'buy':
                    self.next_direction = 'sell'
                else:
                    self.next_direction = 'buy'
                # send opportunity back to the main daemon.
                return ( opp )
            else:
                return None

    # Callback. Daemon calls this when it *SUCCESFULLY* opens a position returned by this strategy.
    # STore the data for future analysis.
    def callback(self, placed_order):
        # The order ID is set in the daemon, before it sends back the order to here.
        self.current_trades.append( placed_order )

    # Callback. Daemon calls this when a position is closed, so this strategy can log data
    # about the trade. Write profit to database, that sort of thing.
    #def callback_close(self):
    #    self.past_orders.append( self.current_order.pop() )


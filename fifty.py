# Fifty-fifty strategy

import oanda
import log
import order

class fifty():

    def __init__(self):
        self.oanda_instance = oanda.oanda()
        self.next_direction = 'buy'
        self.trades = []
        self.is_open_trade = True
        self.current_open_trade = {'order_id':0, 'tp':0, 'sl':0}

    # Look at current price and past prices and determine whether there is an opportunity or not.
    # Returns:
    #   If the daemon should enter a trade, an instance of `order', otherwise
    #   None.
    def refresh(self):
        
        # Perhaps don't bother scanning for entrance opportunities if we are still waiting on
        # another trade to close
        if self.is_open_trade:
            # Babysit open position TODO
            # pull order info
            # adjust SL, TP, expiry, units
            pass
        else:
            spread = round(oanda_instance.get_spread('USD_JPY'),2)
            log.write_to_log('Spread: ', spread)
            if spread < 3:
                # return opportunity
                if self.next_direction == 'buy':
                    cur_ask = round(oanda_instance.get_ask('USD_JPY') ,2)
                    sl = cur_ask - 0.05
                    tp = cur_ask + 0.10
                else:
                    # sell
                    self.next_direction = 'sell'
                    cur_ask = round(oanda_instance.get_ask('USD_JPY') ,2)
                    sl = cur_ask + 0.05
                    tp = cur_ask - 0.10

                # Prepare new opportunity. Everything that will be passed to the REST API is a string.
                opp = opportunity(100, 'USD_JPY', '100', self.next_direction, 'market', '', '', '', '', sl, tp, '')
                # switch direction for next time
                if self.next_direction == 'buy':
                    self.next_direction = 'sell'
                else:
                    self.next_direction = 'buy'
                # send opportunity back to the main daemon.
                return ( {'opp':opp, 'callback_open':self.callback_open, 'callback_close':self.callback_close} )
            else:
                return None

    # Callback. Daemon calls this when it opens a position returned by this strategy.
    # The trade order number is stored here, for self-monitoring purposes.
    # It should also be stored to the database.
    def callback_open(self, order_id):
        self.trades.append(str(order_id))
        self.is_open_trade = True
        self.current_open_order['order_id'] = order_id #TODO store rest of info here, or wait for refresh() to fill it?

    # Callback. Daemon calls this when a position is closed, so this strategy can log data
    # about the trade.
    def callback_close(self):
        # Write profit to database, that sort of thing.
        self.is_open_trade = False



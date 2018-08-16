from backtesting.backtest_broker import BacktestBroker as broker
from datetime import datetime, timedelta
from instrument import Instrument
from log import Log
from opportunity import Opportunity
from order import Order
from strategy import Strategy
from trade import Trade, Trades, TradeClosedReason

class Demo(Strategy):

    num_slots = 10
    price_history = [None]*num_slots # nth element = price n minutes ago
    last_history_update = None # time of last history update
    instrument_ids = [4,5] # these should be passed into the Strategy constructor

    def get_name(self):
        """        Return the name of the strategy."""
        return "Backtest Demo"


    def __str__(self):
        """  """
        return self.get_name()


    def _babysit(self):
        """Monitor open positions. Check if any have closed.
        """
        for otid in self.open_trade_ids:
            if broker.is_closed(otid):
                self.open_trade_ids.remove(otid) # mark status


    def _scan(self):
        """Look for opportunities to open a position.
        Returns:
            [<Opportunity>] if there is an opportunity.
            Empty list if no opportunities.
            None on failure.
        """
        for iid in self.instrument_ids:
            now = broker.get_time()
            spread = broker.get_spread(iid)
            price = broker.get_price(iid)
            goal = spread # goal profit per trade

            # always update the price history
            if self.last_history_update == None or now - self.last_history_update >= timedelta(minutes=1):
                self.last_history_update = now
                # shift everything by one
                for i in range(len(self.price_history)-1, 0, -1):
                    self.price_history[i] = self.price_history[i-1]
                self.price_history[0] = price

            # check for opp
            go = False
            # only if price history completely filled
            if not None in self.price_history:
                smooth = True
                for i in range(0, len(self.price_history)-1):
                    # if more recent price has decreased or stayed same
                    if self.price_history[i] <= self.price_history[i+1]:
                        smooth = False
                rise = self.price_history[0] - self.price_history[self.num_slots-1]
                expectation = 5 * spread
                if smooth and rise > expectation: go = True

            # suggest trade if no open trades
            if go and len(self.open_trade_ids) < 1:
                order = Order(
                    instrument=Instrument(iid),
                    order_type='market',
                    take_profit=self.price_history[0] + goal + spread/float(2), # long
                    stop_loss=self.price_history[0] - goal + spread/float(2),   # long
                    units=1,                                                   # long
                    #take_profit=self.price_history[0] - goal - spread/float(2),  # short
                    #stop_loss=self.price_history[0] + goal - spread/float(2),    # short
                    #units=-1,                                                   # short
                    reason='demo'
                )
                opp = Opportunity(order, conf=1, strat=self, reason='demo')
                return [opp]
            else: 
                return []



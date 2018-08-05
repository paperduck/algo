"""
Backtest entry point. Run this to perform a backtest.
The backtest equivalent of daemon.py.
    $ cd src/
    $ python3 run_backtest.py
"""

# external modules
from datetime import datetime
# internal modules
from backtesting.backtest_broker import BacktestBroker as broker
# strategy to test - import backtesting version, not live version
from backtesting.strategies.demo import Demo as strat


if __name__ == "__main__":
    start = datetime(year=2003, month=1, day=1)
    end = datetime(year=2003, month=2, day=1) # TODO: make sure this is read as UTC - pandas took it as JST?
    #files = {4:'csv/USDJPY.txt', 5:'csv/USDCAD.txt'}
    files = {4:'csv/USDJPY.txt'}
    broker.init(start, end, files)
    while(broker.advance()):
        opps = strat.refresh()
        if len(opps) > 0:
            opp = opps[0]
            trade_id = broker.place_trade(opp.order, opp.order.units) # daemon normally decides units
            # notify strategy
            if trade_id: strat.trade_opened(trade_id)
    

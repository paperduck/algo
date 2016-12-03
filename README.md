#Algorithmic Trading Daemon ("algo")

There are three pieces to this project, as with any algorithmic trading: backtesting, forward testing, and live trading.

## Backtesting
- Backtesting will consist of a MySQL database with historical data. The daemon iterates through the historical data to simulate live trading.
- The backtesting modules will use a strategy module as it is, so that strategy modules are blind to whether they are being used for backtesting or live trading. This eliminates the need to re-write strategy code for backtesting versus live trading.

## Forward Testing
- Same as live trading, except fake money is used.
- The "practice" variable in the config file is toggled to `True`.

## Live Trading
- The main program is referred to as a "daemon", and exists in `daemon.py`.
- Run it like this: `# python3 daemon.py`.
- This utilizes a custom-built API (`oanda.py`), which in turn uses Oanda's REST API. Oanda is the Forex dealer I use. 
- Each strategy gets its own module, for example the `fifty.py` strategy module encapsulates one simple strategy.

## Platform Design
- Everything is designed with scalability and modularity in mind.
- Strategy modules can be used or not used arbitrarily, with only trivial changes to the daemon.
- Strategy modules can be used for backtesting, forward testing, and live trading with only trivial changes to the strategy module.
- The daemon is designed such that it can handle  number of strategies at any given time.



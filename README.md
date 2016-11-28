Algorithmic Trading Daemon ("algo")

There are two pieces to this project; the trading daemon and backtesting.

# Daemon
- Currently the trading daemon exists as a Python script `daemon.py`.
- This utilizes a custom-built API (`oanda.py`), which in turn uses Oanda's REST API. Oanda is the Forex dealer I use. 
- Each strategy gets its own module, for example the `fifty.py` strategy module encapsulates one simple strategy.

# Backtesting
- Backtesting will consist of a MySQL database with historical data and the `backtesting.py` module that iterates through the historical data and simulates live trading.
- The backtesting module will use a strategy module the same way the daemon uses the strategy module, so that strategy modules are blind to whether they are being used for backtesting or live trading. This eliminates the need to re-write strategy code for backtesting versus live trading.

# Platform Design
- Everything is designed with scalability and modularity in mind.
- Once a strategy module passes backtesting, the file can be moved from the backtesting directory into the daemon directory, with only trivial changes to the code.
- The daemon is designed such that it can handle any number of strategies at any given time.


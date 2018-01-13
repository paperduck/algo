# Algorithmic Trading Daemon ("algo")

## Introduction
- This is a work in progress. As of 2017-12-30, live trading and forward testing are being coded. Backtesting is mostly non-existent.
- It is a command line application for Linux. The Debian operating system is being used for development.
- Python is used for the bulk of the program (`/src/`). The database is MySQL (`/src/db/`).
- There are three pieces to this project, as with any algorithmic trading: backtesting, forward testing, and live trading.

## Backtesting
- Backtesting might consist of a feed class that reads in CSV files, then iterates through them. You could then write a backtesting script to simualate your strategy. Or I might use an existing backtesting library.

## Forward Testing
- Same as live trading, except fake money is used.
- For Oanda, this is as simple as toggling the `live_trading` key/value in the public config file to `False`.

## Live Trading
- It is referred to as a "daemon" because it is intended to be self-sufficient and not require monitoring or adjustment.
- Each strategy gets its own module. For example, the `/src/strategies/fifty.py` module encapsulates one simple strategy.
- Toggle the public config `live_trading` key to `True`.

## How to use
- Run the platform from /src/ : `$ python3 main.py`. Press `q` to quit, `m` to update the on-screen statistics.
- It may be helpful to watch the tail of the log file while running the platform: `$ watch 'tail logfile.log'`. The location of the log file is specified in the private config file.
- Run test script from /src/ : `$ bash tests/run_tests.sh`
- You will need to make your own private config file. Put it in a secure location and specify that path in the public config  (`/src/config_nonsecure.cfg`). The key/value pairs you must include in the private config can be determined by reading `/src/config.py`.
- You will need to create the database on your machine. There is a backup script for the purpose of recreating the structure. It is in `/src/db/db_backup.mysql`. It may or may not be up to date.
- Implement strategies by creating your own strategy module in `/src/strategies/`. Inherit the `Strategy` class from `/src/strategy.py` and implement your own logic. Logic for opening positions goes into the `_scan()` method. This is called over and over; if you want to place an order, return an instance of `Opportunity`. Logic for closing positions goes into `_babysit()`.
- The `Chart` class in `/src/chart.py` provides a convenient way to analyze candlesticks and make decisions. In the future I would like to incorporate indicators into this class.

## Platform Design: Scalability and Modularity
- Scalability and user-friendliness take priority over speed. This is not intended to be used for high-frequency trading and/or arbitrage.
- The strategy modules can be used (or not used) arbitrarily. Just modify the startup portion of `daemon.py` to include your module in the list of strategies. Currently you can only choose strategies when the platform is not running, but it would be neat to have strategies be "hot-swappable" in the future.
- Having the generic broker layer allows you to conveniently change the broker you use. If you want to use a broker for which I don't provide a translator module, you can provide your own. You would have to make your translator module such that its methods match those in `broker.py`. You may also have to tweak `broker.py` if you want to add additional functionality.
- With an emphasis on scalability, this platform is intended to handle any number of strategies at any given time. The central daemon module will be responsible for managing things like account balance, order size, and diversification. The disparate strategy modules, which do not communicate with each other, independently suggest trades to the daemon.

Here is a diagram of the layers. The daemon sits on top and talks to the strategies. The daemon and strategies talk to the broker via the broker module, which delegates calls to a specific translator module. The translator modules contain the code that talks directly to brokers' APIs.

![diagram](docs/platform_diagram_2.png)


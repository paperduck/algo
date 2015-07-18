### Introduction

Project "Algo" will be a Linux command-line application for running and monitoring security trading algorithms.

### Status (most recent first)

- July 2015
  - Successfully ran "reversal" strategy simulation with various input parameters. Results are stored in text files, with a summary at the end of each file. Thinking about storing results in MySQL for easier post-simulation analysis.
  - [algo/backtesting/public/reversal](https://github.com/paperduck/algo/tree/master/backtesting/public/reversal)
  - Backtesting instructions can be found in the backtesting README. [(link)](https://github.com/paperduck/algo/blob/master/backtesting/README.md)
- June 2015
  - Developed a few backtesting scripts that run simulations using historical data. 
- June 2015
  - Created scripts to load historical data CSV files into MySQL database. Loaded minute data of the S&P 500.
- 2014-12-6
  - Repo created

### End Goals

- Command-line interface for managing modular trading algorithms.
- Each trading strategy should be implemented as a shared/static library that implements
functionality from the core engine.
- Each strategy should be implemented in its own library, even it uses the same broker API as another strategy.
- Main engine will be independent of any broker API. Broker-specific code will go into each library.
- Example abstract functions used by core engine. These would be implemented in each library.
  - Start()
  - Stop()
  - GetBrokerInfo()
  - GetAccountBalance()
- Central engine manages things like:
  - brokerage account(s), e.g. account balance, margin 
  - risk, exposure
  - trade goals
- Real-time diagnostics available on command line, for example:
  - Account balance
  - Number of strategies currently active
  - Daily goal met (y/n)
  - Performance log
- Toggle between paper trading and live trading

### Technical Specifications

- Intended for Linux operating system.
- C++ latest version will be used for main application.
- MySQL database.
- Scripting languages will be used as appropriate, with preference given to Python, Bash, and Haskell.

### Repository Structure

- [/backtesting/](https://github.com/paperduck/algo/tree/master/backtesting) - backtesting simulation code
  - [/templates/](https://github.com/paperduck/algo/tree/master/backtesting/templates) - template for new backtests
  - [/public/](https://github.com/paperduck/algo/tree/master/backtesting/public) - simulations that can be run
- [/main/](https://github.com/paperduck/algo/tree/master/main) - main appliation code, including command-line interface
- [/modules/](https://github.com/paperduck/algo/tree/master/modules) - trading strategies managed by the main application
- [/scripts/](https://github.com/paperduck/algo/tree/master/scripts) - miscellaneous scripts, such as loading CSV files into database.
  - [load_csv/](https://github.com/paperduck/algo/tree/master/scripts/load_csv) - scripts to load CSV files into database.
- [/symbol_lists/](https://github.com/paperduck/algo/tree/master/symbol_lists) - text list of security symbols, for convenience.



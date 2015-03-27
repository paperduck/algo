### Introduction

Project 'algo' will be a Linux command-line engine for running stock trading algorithms.

### STATUS:

In initial design and development phase.

### Goals

- Command-line interface for managing modular trading algorithms.
- Each trading strategy should be implemented as a shared library that implements
the engine API. If there are multiple strategies implemented using one broker API, 
each strategy should be implemented.
- Independent of any broker API. Broker-specific code will go into each algorithm module.
- API example functions:
  - Start()
  - Stop()
  - GetBrokerId()
  - GetAccountBalance()
- Central engine manages brokerage account(s) and algorithms to control risk and track
investment goals.
- Real-time stats, for example:
  - Account balance
  - Number of strategies currently active
  - Daily goal met (y/n)
  - Performance log
- Toggle between paper trading and live trading


### Technical Specifications

Intended for Linux operating system. C++ 11 is the language of choice, with a MySQL
backend. Scripting languages will be used as deemed appropriate, with
preference given to Python, Bash, and Haskell.

### Created:

2014-12-6

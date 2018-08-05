Backtesting


## Overview

A basic backtesting framework is in place. You can use it to test strategy modules against past price data.

The backtesting framework parallels the main platform. That is, `run_backtest.py` acts as the main control point for backtesting, instead of `daemon.py`. `backtest_broker.py` simulates the `broker.py` module. Finally, the strategy modules that you test will be largely the same as a normal strategy module, but modified to use the backtest broker module instead of the regular `broker.py`.

Multiple CSV files can be used concurrently, if you have a strategy that uses multiple instruments.

## How to Use

To perform a backtest, run `run_backtest.py` like this:

`$ python3 run_backtest.py`

## `run_backtest.py`

Main entry point for backtesting. Before running, edit the file to supply it with your CSV filenames.

## `backtest_broker.py`

You don't really need to do anything with this. It iterates through the CSV file(s) and provides information to `run_backtest.py`.

## `csv_parser.py`

This is a utility module for parsing CSV files. If your CSV file is not being read correctly, you may need to change this.



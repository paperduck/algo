
Use templates as a starting point when developing new backtest scripts.

TODO
- factor in bid/ask spreads, if Pi Trading data doesn't already.
- Take out taxes annually rather than once at end of test.
    Don't tax if there is a loss.
- pass in settlement delay as number of days
    Example: value of 3 for T+3 will cause 3-day delay before funds are avaiable after selling
- Instead of iterating through a list of test values in the backtest caller,
    specify a range and step value.
- Add wash-sale prevention
    "Under the wash-sale rules, if you sell stock for a loss and buy it back
    within 30 days before or after the loss-sale date, the loss cannot be
    immediately claimed for tax purposes."
    URL:    http://www.fool.com/personal-finance/taxes/wash-sales-and-worthless-stock.aspx
- Make 'stop amount' input parameter more customizeable
- Add ability to enlarge candlesticks to an arbitrary time span (e.g. do 5min bars rather than 1min)
- Auto sell at day end (optional) to prevent overnight positions
- When trailing stop is triggered, sell at (max - stop) rather than the new (low) price.
    Maybe throw in a few over-reaches at random for realism's sake.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Backtest Database 
    ~ store results of tests in a way that can be quickly and easily analyzed

    ~ Columns in 'algo_table_backtest_headers'
        - id                        PK: # that increments every new test
        - param_1_description
        - param_2_description
        - ...
        - param_20_description

    ~ Columns in 'algo_table_backtest_results':
        - id                    FK: algo_table_backtest_headers.id
        - instrument_symbol     generic of instrument type?
        - test_start_date
        - test_start_time
        - test_end_date
        - test_end_time
        - num_days_to_test
        - num_settlement_days
        - leverage
        - num_round_trips
        - reason_for_test_end
        - commission_per_trade
        - balance_start         principal
        - tax_due_pct           e.g. 0.20
        - balance_final
        - param_1_value
        - param_2_value
        - ...
        - param_20_value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



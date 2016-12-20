

### TODO
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
- Store results in MySQL for easier post-simulation analysis.
- Add greeks to backtest result summary


### Instructions (last updated 2015-07)

Use templates as a starting point when developing new backtest scripts.

The bash script (e.g. `run_proc.sh`) is run on the command line, passing in simulation
arguments like this:

`$ bash run_proc.sh <un> <pw> <days> <commish> <tax 0.75> <principal>`

More arguments are specified in the bash script itself. To run the simulation
with different arguments, the script may need to be edited.

### Output (last updated 2015-07)

Each set of arguments runs a different simulation.

Each such simulation creates a text file in the `out` directory.

The body of the output file may contain information about the progress of 
the simulation, such as details for each particular trade, or when the
simulation has suspended trading until the next day.

Regardless of the body content, each output file ends with a summary.
The summary can be analyzed by extracting important lines using tools like
grep and regex.

##### Example summary:

```text
[ Parameters ]
Time period: 2004-08-19 11:55:00 to 2007-05-18 09:31:00
           = 1002 days, -02:24:00
Completed 637 round trips.
Principal: $10000.00
Trailing stop amount: 0.3004
Each Commission: $1.00
Minimum # red bars before reversal: 2
Minimum price drop % before reversal: 0.001000000

[ Results ]
Total Commission: $1274.00
Gross Profit: $-2181.76
tax factor = 0.75
Final Balance (Principal & P/L & Commission & Tax): $6544.24
```



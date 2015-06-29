
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



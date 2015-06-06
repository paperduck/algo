STRATEGY

    - pick a stock
    - buy it
    - smallest stop loss possible
    - closest trailing stop possible

VARIABLES

    - start date
    - length of time period (end date)
        + num_trades input parameter
    - How time of trade is decided
        + same time every day
        + input parameter
    - How stock is chosen
        + test file that is a list of symbols
        + iterate through symbols, wrap to beginning
    - commission & fees
    - entry cash amount
    - annual taxes

REMARKS

    - Use `low` and `close` fields to trigger trailing stop

PSEUDO FORMULA FOR GENERIC "CORE" STORED PROC
USE THIS AS CORE OF ALL ATTRITION STRATEGIES

    - sum( TRADE1, TRADE2 , ...) * (tax_rate)

        INPUT 
        - multiple trade "results"

        OUTPUT
        - numeric change to account balance

    - TRADE = (buy price @ datetime) + (sell price @ datetime) + (commission)

        INPUT
        - start date
        - time
        - number trades
        - stock symbol
        - commission

        OUTPUT
        - result = number that represents change to initial balance
    
PSEUDO PROC

    CREATE PROCEDURE core    
    (
        IN in_start_date
        IN in_trade_time
        IN in_num_trades
        #IN in_symbol
        IN symbol_list_file
        IN in_commission
        IN tax_factor # e.g. 0.75
    )
    BEGIN
        -- get first entry point
        create iter at row
        where date = in_start_date
        where time = soonest after in_trade_time
        in stock_${in_symbol | tr upper:lower}
        num_round_trips = 0        

        while num_round_trips < in_num_trades:
        {
            buy_price = `open`
            if `low` < buy_price then:
                sell_price = `low`
                log sell
                break
            if `close` < buy_price then:
                sell_price = `close`
                log sell
                break
            while 1:
                increment iter (order by date asc, time asc)
                if `open` < buy_price then:
                    sell_price = `open`
                    log sell
                    break
                if `low` < buy_price then:
                    sell_price = `low`
                    log sell
                    break
                if `close` < buy_price then:
                    sell_price = `close`
                    log sell
                    break
            log results somewhere
            iterate to next day, in_start_time
            if ran out of historical data:
                log warning
                break
        }
    END


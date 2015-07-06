#!/usr/bin/bash

# validate input arguments
if [[ $# -ne 3 ]]; then
    printf "%s\n" "bash $0 <mysql username> <mysql pw> <table name>"
    exit 1
fi

u=$1
pw=$2
table_name=$3 

query="
delimiter //
DROP PROCEDURE IF EXISTS algo.backtest;
CREATE PROCEDURE algo.backtest
(
    IN in_start_date            DATE,
    IN in_num_days              INT,                            -- number of days to trade for (includes market closed days, i.e. weekends)
    IN in_commission            DECIMAL(12,10),                 -- no @
    IN in_tax_factor            DECIMAL(3,2),                   -- e.g. 0.75
    IN in_principal             DECIMAL(10,2),
    IN in_stop_pct              DECIMAL(10,8),                  -- trailing stop percent (% as decimal)
    -- strategy specific:
    IN in_num_pre_swing_bars_needed         INT,
    IN in_min_pre_drawdown_pct              DECIMAL(10,9),
    IN in_min_upswing_percent               DECIMAL(10,9)
)
main_proc: BEGIN
    -- field variables for fetching
    DECLARE cur_date            DATE;
    DECLARE cur_time            TIME;
    DECLARE cur_open            DECIMAL(11,4);
    DECLARE cur_high            DECIMAL(11,4);
    DECLARE cur_low             DECIMAL(11,4);
    DECLARE cur_close           DECIMAL(11,4);
    -- other variables
    DECLARE balance             DECIMAL(11,4)   DEFAULT 0;
    DECLARE open_1              DECIMAL(11,4)   DEFAULT 0;
    DECLARE open_2              DECIMAL(11,4)   DEFAULT 0;
    DECLARE open_3              DECIMAL(11,4)   DEFAULT 0;
    DECLARE cur_n               INT             DEFAULT 1;
    DECLARE sell_date           DATE            DEFAULT NULL;   --
    DECLARE first_fetch_date    DATE            DEFAULT NULL;   -- first date in data set 
    DECLARE first_fetch_time    TIME            DEFAULT NULL;   -- first time in data set 
    DECLARE finding_entry_date  DATE            DEFAULT NULL;   -- 
    DECLARE num_trades_done     INT             DEFAULT 0;      -- no @
    DECLARE buy_price           DECIMAL(11,4)   DEFAULT -1;
    DECLARE buy_date            DATE            DEFAULT NULL;
    DECLARE buy_time            TIME            DEFAULT NULL;
    DECLARE sell_price          DECIMAL(11,4)   DEFAULT -1;
    DECLARE num_shares          INT             DEFAULT 0;
    DECLARE max_price_so_far    DECIMAL(11,4)   DEFAULT -1;
    DECLARE fetch_done          BOOL            DEFAULT FALSE;
    DECLARE gross_profit        DECIMAL(10,2)   DEFAULT 0;
    DECLARE commission_total    DECIMAL(20,10)  DEFAULT 0;
    DECLARE stop_amt            DECIMAL(11,4)   DEFAULT 0;
    -- strategy specific
    DECLARE num_pre_swing_bars_so_far   INT             DEFAULT 0;
    DECLARE downswing_peak              DECIMAL(11,4)   DEFAULT 0;
    DECLARE pre_swing_drawdown_amt      DECIMAL(11,4)   DEFAULT 0;
    -- cursor
    DECLARE curs CURSOR FOR SELECT date, time, open, high, low, close
        FROM $table_name
        WHERE date >= in_start_date
        ORDER BY date ASC, time ASC;
    -- handler
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET fetch_done = TRUE;

    -- Initialize
    OPEN curs;
    SET balance = in_principal;

    -- fetch first row
    FETCH curs INTO cur_date, cur_time, cur_open, cur_high, cur_low, cur_close;
    IF fetch_done THEN
        SELECT 'WARNING: No first row';
        LEAVE main_proc;
    END IF;
    SET first_fetch_date = cur_date;
    SET first_fetch_time = cur_time;
    SELECT CONCAT('First fetch at ', first_fetch_date, ' ', first_fetch_time);

    -- Lazy (static) stop amount. xxx
    SET stop_amt = cur_open * in_stop_pct;
    IF stop_amt < 0.01 THEN
        SET stop_amt = 0.01;
    END IF;

    loop_trade: LOOP
        -- find entry point
        loop_find_entry: LOOP

            -- -------------------------------------------------------------------\
            -- Reversal - Going Long
            -- Inputs:
            --      + bar resolution (one minute assumed for now)
            --      + in_num_pre_swing_bars_needed
            --      + in_min_pre_drawdown_pct
            -- Variables: 
            --      + num_pre_swing_bars_so_far         default:0
            --      + downswing_peak                    default:whatever
            --      + pre_swing_drawdown_amt            default:0
            -- Conditions for Entry:
            --      4. currently in an upswing
            --      1. (open >= close) for 'in_num_pre_swing_bars_needed' bars
            --      2. total drawdown of all 'pre-swing' bars > 'in_min_drawdown_percent'
            --      3. followed by bar with (open - close) of at least 'in_min_pre_drawdown_pct' percent.

            -- 4. check for price increase
            IF cur_close > cur_open THEN
                -- SELECT ''; -- debugging
                -- SELECT CONCAT('closed higher: ', cur_open, ' --> ', cur_open); -- debugging
                
                -- 1. check duration of preceeding downswing
                IF (num_pre_swing_bars_so_far >= in_num_pre_swing_bars_needed) THEN
                    SELECT CONCAT(num_pre_swing_bars_so_far, ' red bars >= ', in_num_pre_swing_bars_needed, ' needed.');
                    -- 2. check downswing percent
                    IF (pre_swing_drawdown_amt / cur_open) > in_min_pre_drawdown_pct THEN
                        SELECT CONCAT('downswing amt (', pre_swing_drawdown_amt, ') / open (', cur_open, ') > min down % (', in_min_pre_drawdown_pct, ')' );
                        SELECT CONCAT('    i.e. ', (pre_swing_drawdown_amt / cur_open), ' > ', in_min_pre_drawdown_pct);
                        -- 3. check upswing percent
                        IF ((cur_close - cur_open) / cur_open) > in_min_upswing_percent THEN
                            SELECT CONCAT('close (', cur_close, ') - open (', cur_open, ') / open (', cur_open, ') > min up % (', in_min_upswing_percent, ')' );
                            -- buy
                            LEAVE loop_find_entry;
                        END IF;
                    ELSE
                        SELECT CONCAT('not enough pre-drop %: ', pre_swing_drawdown_amt / cur_open, ' (actual) < ', in_min_pre_drawdown_pct, ' (needed)' );
                    END IF;
                END IF;

                -- reset the downswing scanner
                SET num_pre_swing_bars_so_far = 0;
                SET downswing_peak = 0; -- this is an important flag that means the peak should be reset.
                SET pre_swing_drawdown_amt = 0;

            ELSE
                -- this bar contributed to a downswing
                -- SELECT CONCAT('closed lower: ', cur_open, ' --> ', cur_close); -- debugging
                SET num_pre_swing_bars_so_far = num_pre_swing_bars_so_far + 1;
                SELECT CONCAT('downswing bars increased to ', num_pre_swing_bars_so_far); -- debugging
                IF downswing_peak = 0 THEN
                    -- new peak
                    SET downswing_peak = cur_open;
                END IF;
                SET pre_swing_drawdown_amt = downswing_peak - cur_close;
            END IF;
            -- -------------------------------------------------------------------/

            -- don't try to enter late in the day
            IF cur_time > '15:30:00' THEN -- 'hh:mm:ss' 24 hour time
                -- Wait until next day
                SET finding_entry_date = cur_date;
                SELECT 'Late in day. Skipping to tomorrow.';
                loop_goto_tomorrow: LOOP
                    FETCH curs INTO cur_date, cur_time, cur_open, cur_high, cur_low, cur_close;
                    IF fetch_done THEN
                        SELECT 'No more data (4)';
                        LEAVE loop_trade;
                    END IF;
                    IF DATEDIFF(cur_date, finding_entry_date) >= 1 THEN
                        LEAVE loop_goto_tomorrow;
                    END IF;
                END LOOP; -- loop_goto_tomorrow
                SELECT 'Reached beginning of tomorrow.';

                -- reset entry point scanning 
                SET num_pre_swing_bars_so_far = 0;
                SET downswing_peak = 0; -- this is an important flag that means the peak should be reset.
                SET pre_swing_drawdown_amt = 0;

            END IF;

            -- fetch next row
            FETCH curs INTO cur_date, cur_time, cur_open, cur_high, cur_low, cur_close;
            IF fetch_done THEN
                SELECT 'No more data (3)';
                LEAVE loop_trade;
            END IF;
            -- SELECT CONCAT('Comparing ', first_fetch_date, ' and ', cur_date, ' (x)');
            IF DATEDIFF(cur_date, first_fetch_date) > in_num_days THEN
                SELECT CONCAT('Num days elapsed (', DATEDIFF(cur_date, first_fetch_date), ') exceeded threshold (', in_num_days, '). (1)');
                LEAVE loop_trade;
            END IF;

        END LOOP; -- loop_find_entry

        SELECT 'Entry point found.';
        SELECT CONCAT('    downswing_peak = ', downswing_peak); -- debugging

        -- fetch next row, which will be entered
        FETCH curs INTO cur_date, cur_time, cur_open, cur_high, cur_low, cur_close;
        IF fetch_done THEN
            SELECT 'No more data (3)';
            LEAVE loop_trade;
        END IF;

        -- enter position
        SET buy_price = cur_open;
        SET buy_date = cur_date;
        SET buy_time = cur_time;
        SET max_price_so_far = buy_price;
        SET num_shares = (balance / buy_price) - 1; -- TODO: improve this approximation
        IF num_shares < 0 THEN
            SET num_shares = 0;
        END IF;
        SET gross_profit = gross_profit - (buy_price * num_shares);
        SET balance = balance - (buy_price * num_shares);
        SET balance = balance - in_commission;
        SELECT CONCAT('BUY  ', num_shares, ' ${table_name} @ ', buy_price, ' on ', cur_date, ' ', cur_time);

        -- fetch next row
        FETCH curs INTO cur_date, cur_time, cur_open, cur_high, cur_low, cur_close;
        IF fetch_done THEN
            SELECT 'No more data (3)';
            LEAVE loop_trade;
        END IF;

        -- loop until position exited
        loop_find_exit: LOOP
            -- trailing stop
            IF  (max_price_so_far - cur_open) >= stop_amt THEN
                SET sell_price = cur_open;
                SELECT CONCAT('SELL ', num_shares, ' ${table_name} @ ', sell_price, ' on ', cur_date, ' ', cur_time);
                -- SELECT CONCAT('    $', ((sell_price - buy_price) * num_shares), ' over ',
                --    DATEDIFF(cur_date, buy_date), ' day(s) and ', TIMEDIFF(cur_time, buy_time));
                SET gross_profit = gross_profit + (sell_price * num_shares);
                SET balance = balance + (num_shares * sell_price);
                SET balance = balance - in_commission;
                SET sell_date = cur_date;
                LEAVE loop_find_exit;
            END IF;
            IF (max_price_so_far - cur_low) >= stop_amt THEN
                SET sell_price = cur_low;
                SELECT CONCAT('SELL ', num_shares, ' ${table_name} @ ', sell_price, ' on ', cur_date, ' ', cur_time);
                -- SELECT CONCAT('    $', ((sell_price - buy_price) * num_shares), ' over ',
                --    DATEDIFF(cur_date, buy_date), ' day(s) and ', TIMEDIFF(cur_time, buy_time));
                SET gross_profit = gross_profit + (sell_price * num_shares);
                SET balance = balance + (num_shares * sell_price);
                SET balance = balance - in_commission;
                SET sell_date = cur_date;
                LEAVE loop_find_exit;
            END IF;
            -- Don't know if the high happens before the low,
            -- but we do know that the high happens before (or on) the close.
            -- So record the max after the open and low, but before the close.
            SET max_price_so_far = cur_high;
            IF (max_price_so_far - cur_close) >= stop_amt THEN
                SET sell_price = cur_close;
                SELECT CONCAT('SELL ', num_shares, ' ${table_name} @ ', sell_price, ' on ', cur_date, ' ', cur_time);
                -- SELECT CONCAT('    $', ((sell_price - buy_price) * num_shares), ' over ',
                --    DATEDIFF(cur_date, buy_date), ' day(s) and ', TIMEDIFF(cur_time, buy_time));
                SET gross_profit = gross_profit + (sell_price * num_shares);
                SET balance = balance + (num_shares * sell_price);
                SET balance = balance - in_commission;
                SET sell_date = cur_date;
                -- IF ABS((sell_price - buy_price)*num_shares) = 0 THEN
                --     SELECT cur_date, ' ', cur_time, ' ', cur_open, ' ', cur_high, ' ', cur_low, ' ', cur_close;
                -- END IF;
                LEAVE loop_find_exit;
            END IF;

            -- Fetch next row
            FETCH curs INTO cur_date, cur_time, cur_open, cur_high, cur_low, cur_close;
            IF fetch_done THEN
                SELECT 'No more data (1)';
                SELECT CONCAT('Ended (while seeking exit) at ', cur_date);
                LEAVE loop_trade;
            END IF;
            -- SELECT CONCAT('Comparing ', first_fetch_date, ' and ', cur_date, '  (w)');
            IF DATEDIFF(cur_date, first_fetch_date) > in_num_days THEN
                SELECT CONCAT('Num days elapsed (', DATEDIFF(cur_date, first_fetch_date), ') exceeded threshold (', in_num_days, '). (2)');
                LEAVE loop_trade;
            END IF;

        END LOOP; -- loop_find_exit

        -- round trip report
        -- xxx maybe not

        -- Any money left?
        IF balance <= in_commission THEN
            SELECT 'ABORT ~ Principal used up.';
            LEAVE loop_trade;
        END IF;

        -- tally trades
        SET num_trades_done = num_trades_done + 1;

        -- Wait until next day
        SELECT CONCAT('Waiting until next day (current date: ', cur_date, ')');
        loop_c: LOOP
            FETCH curs INTO cur_date, cur_time, cur_open, cur_high, cur_low, cur_close;
            IF fetch_done THEN
                SELECT 'No more data (2)';
                LEAVE loop_trade;
            END IF;
            IF DATEDIFF(cur_date, sell_date) >= 1 THEN
                LEAVE loop_c;
            END IF;
        END LOOP; -- loop_c
        SELECT CONCAT('Next day reached (current date: ', cur_date, ')');
        SELECT '';

    END LOOP; -- loop_trade

    -- Report ------------------------------------------------------------------------\

    -- [ Parameters ]

    SELECT '';
    SELECT '[ Parameters ]';
    SELECT CONCAT('Time period: ', first_fetch_date, ' ', first_fetch_time, ' to ', cur_date, ' ', cur_time);
    SELECT CONCAT('           = ', DATEDIFF(cur_date, first_fetch_date), ' days, ', TIMEDIFF(cur_time, first_fetch_time) );
    SELECT CONCAT('Completed ', num_trades_done, ' round trips.');
    SELECT CONCAT('Principal: $', ROUND(in_principal, 2) );
    SELECT CONCAT('Trailing stop amount: ', stop_amt);
    SELECT CONCAT('Each Commission: $', ROUND(in_commission, 2) );
    -- strategy specific
    SELECT CONCAT('Minimum # red bars before reversal: ', in_num_pre_swing_bars_needed);
    SELECT CONCAT('Minimum price drop % before reversal: ', in_min_pre_drawdown_pct);

    -- [ Results ]

    SELECT '';
    SELECT '[ Results ]';
    SET commission_total = (in_commission * num_trades_done * 2);
    -- total commission
    SELECT CONCAT('Total Commission: $', ROUND(commission_total, 2) );
    -- gross profit
    SELECT CONCAT('Gross Profit: $', ROUND(gross_profit, 2) );
    -- take out income tax, if profit (not loss)
    SELECT CONCAT('tax factor = ', in_tax_factor);
    -- final balance
    IF gross_profit > 0 THEN
        SET balance = balance - ( gross_profit * (1 -in_tax_factor) );
    END IF;
    SELECT CONCAT('Final Balance (Principal & P/L & Commission & Tax): $', ROUND(balance, 2) );
    SELECT '----------------------------';

    -- -------------------------------------------------------------------------------/
END
"
mysql -u$u -p$pw algo -e "${query}"

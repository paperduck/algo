#! /bin/bash

printf "$(date)\n\n" > dout.txt

#AUTH="$(head -n 1 /home/user/raid/documents/oanda_token.txt)"
AUTH="$(head -n 1 /home/user/raid/documents/oanda_practice_token.txt)"
#URL='https://api-fxtrade.oanda.com'
URL='https://api-fxpractice.oanda.com'


# Get account info
ACCOUNTS=$(curl -H "Authorization: Bearer $AUTH" "$URL/v1/accounts")
# verify OK
if [ "$(printf "$ACCOUNTS" | jq '.code')" = "null" ]
then
    printf "ACCOUNTS response OK\n" >> dout.txt
else
    printf "Error (failed to get account info):\n$ACCOUNTS\n(end)\n" >> dout.txt
    exit 0
fi

### debugging ###
printf "$ACCOUNTS"
cat dout.txt
exit 0
#################

# get primary account number
ACCOUNT_ID_PRIMARY=$(\
printf "$ACCOUNTS" | jq \
'.accounts[] | if .accountName == "Primary" then .accountId else empty end')
# verify OK
if [ "$ACCOUNT_ID_PRIMARY" != "" ]
then
    printf "ACCOUNT_ID_PRIMARY response OK\n" >> dout.txt
else
    printf "Error (failed to get ID of primary account):\n($ACCOUNT_ID_PRIMARY)\n(end)\n" >> dout.txt
    exit 0
fi

# get primary account info
PRIMARY_ACCOUNT=$(\
curl -s -H "Authorization: Bearer $AUTH" \
"$URL/v1/accounts/$ACCOUNT_ID_PRIMARY")
# verify OK
if [ "$(printf "$PRIMARY_ACCOUNT" | jq '.code')" = "null" ]
then
    printf "PRIMARY_ACCOUNT response OK\n" >> dout.txt
else
    printf "Error (failed to get info of primary account):\n$PRIMARY_ACCOUNT\n(end)\n" >> dout.txt
    exit 0
fi

# Get position info
POSITIONS=$(\
curl -s -H "Authorization: Bearer $AUTH" \
"$URL/v1/accounts/$ACCOUNT_ID_PRIMARY/positions")
# verify OK
if [ "$(printf "$POSITIONS" | jq '.code')" = "null" ]
then
    printf "POSITIONS response OK\n" >> dout.txt
else
    printf "Error (failed to get position info):\n$POSITIONS\n(end)\n" >> dout.txt
    exit 0
fi

# Get number of positions
NUM_OF_POSITIONS=$(\
printf "$POSITIONS" | jq '.positions | length')

# Get balance
BALANCE=$(\
printf "$PRIMARY_ACCOUNT" | jq \
'.balance')

# get spread (USD JPY)
PRICE_USDJPY=$(\
curl -s -H "Authorization: Bearer $AUTH" \
"$URL/v1/prices?instruments=USD_JPY")
BID_USDJPY=$(printf "$PRICE_USDJPY" | jq '.prices[0].bid')
ASK_USDJPY=$(printf "$PRICE_USDJPY" | jq '.prices[0].ask')
SPREAD_USDJPY=$(echo "($ASK_USDJPY - $BID_USDJPY) * 100" | bc)

#Dump
printf "\n" >> dout.txt
#printf "$(date)    accounts:\n---------------\n$ACCOUNTS\n(end)\n" >> dout.txt
#printf "$(date)    primary account:\n---------------\n$PRIMARY_ACCOUNT\n(end)\n" >> dout.txt
printf "$(date)    primary account number: $ACCOUNT_ID_PRIMARY\n" >> dout.txt
printf "$(date)    balance: $BALANCE\n" >> dout.txt
printf "$(date)    num of pos's = $NUM_OF_POSITIONS\n" >> dout.txt
printf "$(date)    USD/JPY ask: $ASK_USDJPY\n" >> dout.txt
printf "$(date)    USD/JPY buy: $BID_USDJPY\n" >> dout.txt
printf "$(date)    USD/JPY spread: $SPREAD_USDJPY\n" >> dout.txt

if [ $(echo "$SPREAD_USDJPY < 3" | bc) -eq "1" ]
then
    printf "$(date)    spread OK\n" >> dout.txt
    # Calculate Stop Loss
    # bc scale has to be set inline to allow for decimal quotient.
    BID_ASK_AVG=$(echo "scale=5; ($ASK_USDJPY + $BID_USDJPY) / 2" | bc)
    printf "$(date)    bid ask average: $BID_ASK_AVG\n" >> dout.txt
    # stop loss price (change to minus for BUY)
    SL_PRICE=$(echo "scale=5; $BID_ASK_AVG + 0.1" | bc)
    # truncate to two decimal places
    SL_PRICE=$( echo "scale=2; $SL_PRICE / 1" | bc)
    printf "$(date)    SL price = $SL_PRICE\n" >> dout.txt

    # take profit price (change to plus for BUY)
    TP_PRICE=$(echo "scale=5; $BID_ASK_AVG - 0.15" | bc)
    # truncate to two decimal places
    TP_PRICE=$( echo "scale=2; $TP_PRICE / 1" | bc)
    printf "$(date)    TP price = $TP_PRICE\n" >> dout.txt

    printf "$(date)    URL = $URL/v1/accounts/$ACCOUNT_ID_PRIMARY/orders?\
instrument=USD_JPY&units=33&side=sell&type=market&trailingStop=$SL_PRICE&takeProfit=$TP_PRICE\n" >> dout.txt
    cat dout.txt
    exit 0

    # Submit order
    RESPONSE=$(\
        curl -s -X POST -H "Authorization: Bearer $AUTH" \
        -d "instrument=USD_JPY&units=33&side=sell&type=market&trailingStop=$SL_PRICE&takeProfit=$TP_PRICE" \
        "$URL/v1/accounts/$ACCOUNT_ID_PRIMARY/orders"
        )
    printf "\n$(date)    order response:\n$RESPONSE\n(end of response)\n" >> dout.txt

else
    printf "spread too high\n"
fi
exit 0




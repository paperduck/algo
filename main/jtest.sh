#! /bin/sh
printf "$(date)"'\n\n' > dout.txt

AUTH="ce4a8ac607a3dc03b5d79a8c4718d3c4-f76d1db8e2efba5ff6cfff2af172a45a"

# get primary account number
ACCOUNT_ID_PRIMARY=$(\
curl -s -H "Authorization: Bearer $AUTH" \
https://api-fxtrade.oanda.com/v1/accounts | jq \
'.accounts[] | if .accountName == "Primary" then {primary: .accountId} else empty end | .primary'\
)

# get spread (USD JPY)
PRICE_USDJPY=$(\
curl -s -H "Authorization: Bearer $AUTH" \
"https://api-fxtrade.oanda.com/v1/prices?instruments=USD_JPY"
)
BID_USDJPY=$("printf $PRICE_USDJPY | jq '.prices[0].bid'")

ASK_USDJPY=$("printf $PRICE_USDJPY | jq '.prices[0].ask'")

SPREAD_USDJPY=${$ASK_USDJPY - $BID_USDJPY}
printf "\nspread:  $SPREAD_USDJPY\n"

#curl -s -H "Authorization: Bearer ce4a8ac607a3dc03b5d79a8c4718d3c4-f76d1db8e2efba5ff6cfff2af172a45a" \
#-X GET https://api-fxtrade.oanda.com/v1/accounts/$ACCOUNT_ID_PRIMARY/trades
#printf '\n\n'

exit 0

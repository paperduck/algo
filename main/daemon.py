#!/usr/bin/python3
# Python 3.4

#--------------------------
import datetime
import sys
import urllib.request
import urllib.error
import time
#from jq import jq
import json
#--------------------------
LOG_PATH = 'dout.txt'
PRACTICE = True

#--------------------------
# clear log
def clear_log():
    with open(LOG_PATH, 'w') as f:
        f.write('')
        f.close()

# append to log
def write_to_log(str):
    with open('dout.txt', 'a') as f:
        f.write(str)
        f.close()

# Get authorization key.
# Oanda was returning a '400 Bad Request' error 4 out of 5 times
#   until I removed the trailing '\n' from the string
#   returned by f.readline().
def get_auth_key():
    if PRACTICE:
        with open('/home/user/raid/documents/oanda_practice_token.txt', 'r') as f:
            auth = f.readline()
            auth = auth.rstrip()
            f.close()
        return auth
    else:
        with open('/home/user/raid/documents/oanda_token.txt', 'r') as f:
            auth = f.readline()
            auth = auth.rstrip()
            f.close()
        return auth

def get_rest_url():
    if PRACTICE:
        return 'https://api-fxpractice.oanda.com'
    else:
        return 'https://api-fxtrade.oanda.com'
 
#--------------------------
clear_log()
write_to_log( datetime.datetime.now().strftime("%c") + "\n\n" )
print (get_auth_key())
print (get_rest_url())

# get account info
headers = {'Authorization': 'Bearer ' + get_auth_key(), 'Content-Type': 'application/x-www-form-urlencoded'}
req = urllib.request.Request(get_rest_url() + '/v1/accounts', None, headers)
"""
print ("full url:      ", req.full_url)
print ("URI scheme:    ", req.type)
print ("URI authority: ", req.host)
print ("data:          ", req.data)
print ("headers:       ", req.header_items())
"""
try:
    response = urllib.request.urlopen(req)
    #print ("RESPONSE URL: ", response.geturl())
    #print ("RESPONSE INFO:", response.info())
    #print ("RESPONSE CODE: ", response.getcode())
    json_accounts = response.read()
    print ("JSON:\n", json_accounts)
except (urllib.error.URLError):
    print ("URLError:", sys.exc_info()[0])
    print ("EXC INFO: ", sys.exc_info()[1])
except:
    print ("other error:", sys.exc_info()[0])


"""
# 2016-09: Getting '400: Bad Request' responses 4 out of 5 times, so adding a retry loop here
num_tries = 0
try_limit = 100
delay = 1   # seconds
start = time.time()
for i in range(0, try_limit):
    print ("Attempt #", num_tries)
    req = urllib.request.Request(get_rest_url() + '/v1/accounts', None, headers={'Authorization': 'Bearer ' + get_auth_key()})
    try:
        response = urllib.request.urlopen(req)
        print ("RESPONSE URL: ", response.geturl())
        print ("RESPONSE INFO:", response.info())
        print ("RESPONSE CODE: ", response.getcode())
        json_accounts = response.read()
        print ("JSON:\n", json_accounts)
        break
    except (urllib.error.URLError):
        print ("URLError:", sys.exc_info()[0])
        print ("EXC INFO: ", sys.exc_info()[1])
    except:
        print ("other error:", sys.exc_info()[0])
    num_tries = num_tries + 1
    checkpoint = time.time()
    while (checkpoint - start < delay):
        checkpoint = time.time()
        time.sleep(1)
    print ("Slept for ", (checkpoint - start), " seconds.")
    start = time.time()
    delay = delay + 1
"""

#json_account_id_primary = json.loads(json_accounts)
#print ("JSON ACCOUNT ID PRIMARY:\n", json_account_id_primary, "\n")

"""

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
"""



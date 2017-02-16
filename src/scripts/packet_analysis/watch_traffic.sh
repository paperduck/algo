# network packet monitor to verify data to/from broker.
# SIGINT (Ctl-C) to exit.


# -A    print packet in ASCII
# -e    print link-layer header
# -i    listen on <interface>
# -l    line buffered for easier reading of live stream
# -#    print packet number at beginning of line
# -q    quiet
# -Q    direction: 'in', 'out', or 'inout'
# -t    no timestamp
# -v    verbose
# -vv
# -vvv
# -w    write to <file>
# <expression   a pcap filter; see 
#               man pcap-filter(7)

tcpdump -e -q -# -t -w watch_out.txt -i eth0

#tcpdump -A -e -vvv -# -t -w watch_out.txt dst host 'api-fxpractice.oanda.com'


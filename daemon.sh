#! /bin/sh
#
#

### BEGIN INIT INFO
# Provides:             daemon.sh
# Required-Start:       
# Required-Stop:        
# X-Start-Before:   
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description: algo daemon
# Description: algo daemon
### END INIT INFO

SUBJECT='Have a nice day.'
BODY="
$(who -r)

Sincerely,
  $(whoami)"

case "$1" in
  start)
        # send email
        python /home/user/raid/software_projects/algo/scripts/emailer.py "$SUBJECT" "$BODY"
        ;;
esac


exit 0

#/usr/bin/env python

import smtplib


server = smtplib.SMTP("localhost", 587)
server.set_debuglevel(True)
server.ehlo()
if server.has_extn('STARTTLS'):
    print "\ryes"
    server.starttls()
    print "\rstarted tls"
    server.ehlo()
    print "\rok"
else:
    print "\rno"



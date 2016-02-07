#!/usr/bin/env python 

import cgi
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
#import ldap
import mimetypes
#apache_mimetypes = mimetypes.MimeTypes(['/etc/mime.types'])
import multiprocessing
import os
import smtplib
import sys
import traceback

to_addr = "quackman@hotmail.com"
from_addr = "test@deb.home"
body_text = "auto email test"
message = MIMEText(body_text)
message["Subject"] = "subject"
message["From"] = from_addr
message["To"] = to_addr
message["Return-Path"] = "<test@deb.home>"
message["Auto-Submitted"] = "auto-generated"
#smtp = smtplib.SMTP("localhost")
#smtp = smtplib.SMTP("localhost", 587)
#smtp = smtplib.SMTP("localhost", 666)
#smtp = smtplib.SMTP("localhost", 25)
#smtp = smtplib.SMTP("localhost", 2525)
#alternative ports from docomo support: 587, 465(SSL)  
#s = smtplib.SMTP("smtp.gmail.com", 587, localhostname)
smtp = smtplib.SMTP("localhost", 587)
#smtp = smtplib.SMTP_SSL("localhost", 465)
try:
    print("starting tls...")
    smtp.starttls()
    print("sending email")
    smtp.sendmail(from_addr, [to_addr], message.as_string())  #body_text)
    print("sent email")
except Exception, em:
    print("ERROR(Exception): " + str(em) )
except SMTPException, em:
    print("ERROR(SMTPException): " + str(em) )
smtp.quit()

#EOF

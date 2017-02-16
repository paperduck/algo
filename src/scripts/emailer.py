#!/usr/bin/env python 

import cgi
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
#apache_mimetypes = mimetypes.MimeTypes(['/etc/mime.types'])
import multiprocessing
import os
import smtplib
import sys
import traceback

if len(sys.argv) != 3:
    print ('usage:  python emailer.py <subject> <body>')
    quit()
with open('/home/user/raid/documents/algo_from_addr.txt', 'r') as f:
    from_addr = f.readline()
    from_addr = from_addr.rstrip()
    f.close()
with open('/home/user/raid/documents/algo_from_pw.txt', 'r') as f:
    from_pw = f.readline()
    from_pw = from_pw.rstrip()
    f.close()
with open('/home/user/raid/documents/algo_to_addr.txt', 'r') as f:
    to_addr = f.readline()
    to_addr = to_addr.rstrip()
    f.close()
body_text = sys.argv[2]
message = MIMEText(body_text)
message["Subject"] = sys.argv[1]
message["From"] = from_addr
message["To"] = to_addr
message["Return-Path"] = "localhost"
message["Auto-Submitted"] = "auto-generated"
#smtp = smtplib.SMTP("localhost")
#smtp = smtplib.SMTP("localhost", 587)
#smtp = smtplib.SMTP("localhost", 666)
#smtp = smtplib.SMTP("localhost", 25)
#smtp = smtplib.SMTP("localhost", 2525)
#alternative ports from docomo support: 587, 465(SSL)  
#s = smtplib.SMTP("smtp.gmail.com", 587, localhostname)
#returns a response code or exception
#smtp = smtplib.SMTP("localhost")
#smtp = smtplib.SMTP("localhost", 465)
smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
try:
    print("logging in...")
    smtp.login(from_addr, from_pw)
    print("sending email")
    smtp.sendmail(from_addr, [to_addr], message.as_string())  #body_text)
    print("sent email")
except Exception as em:
    print("ERROR(Exception): " + str(em) )
#except SMTPException, em:
except:
    print("ERROR (other): " + str(em) )
print ("quitting")
smtp.quit()


#!/usr/bin/python3

# log.py
# for logging output
# Python 3.4

import datetime

log_path = 'output.txt'

# clear log
def clear_log():
    with open(log_path, 'w') as f:
        f.write('')
        f.close()

# append to log
def write_to_log(*args):
    arg_list = list(args)
    dt = datetime.datetime.now().strftime("%c")
    msg = '\n' + dt + '    '
    for a in arg_list:
        msg = msg + str(a)
    with open(log_path, 'a') as f:
        f.write(msg)
        f.close()


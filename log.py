#!/usr/bin/python3

# log.py
# for logging output
# Python 3.4

import datetime

class log():

    def __init__(self, in_enabled = True):
        self.log_path = 'output.txt'
        self.enabled = in_enabled

    # clear log
    def clear(self):
        with open(self.log_path, 'w') as f:
            f.write('')
            f.close()

    # append to log
    def write(self, *args):
        if self.enabled:
            arg_list = list(args)
            dt = datetime.datetime.now().strftime("%c")
            msg = '\n' + dt + '    '
            for a in arg_list:
                msg = msg + str(a)
            with open(self.log_path, 'a') as f:
                f.write(msg)
                f.close()


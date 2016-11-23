#!/usr/bin/python3

# File          log.py
# Python ver.   3.4
# Description   For logging output

import configparser
import datetime


# TODO: add mutex so multiple threads can use this at the same time.
class log():

    cfg = configparser.ConfigParser()
    cfg.read('/home/user/raid/documents/algo.cfg')
    log_path = cfg['log']['file']

    # clear log
    @classmethod
    def clear(cls):
        with open(cls.log_path, 'w') as f:
            f.write('')
            f.close()

    # append to log
    @classmethod
    def write(cls, *args):
        arg_list = list(args)
        dt = datetime.datetime.now().strftime("%c")
        msg = '\n' + dt + '    '
        for a in arg_list:
            msg = msg + str(a)
        with open(cls.log_path, 'a') as f:
            f.write(msg)
            f.close()

    # save info about a transaction
    @classmethod
    def transaction(cls, trans_id):
        # TODO: retrieve transaction info and write it to database
        cls.write('"log.py" in transaction(): Saving transaction info to database. ID: ', trans_id)



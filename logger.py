#!/usr/bin/python3

# File          log.py
# Python ver.   3.4
# Description   For logging output
# How to use
#   Import the class from the module and call the static (class) methods.
#   The log file is specified in the config file.
# Remarks
#   Theoretically, important stuff will be saved in the database, not a log file.
#   So everything shares the same log file because it's not too important to have separate log files.

#*************************
import configparser
import datetime
#*************************
#*************************


# TODO: add mutex so multiple threads can use this at the same time.
class log():

    cfg = configparser.ConfigParser()
    cfg.read('/home/user/raid/documents/algo.cfg')
    log_path = cfg['log']['path']
    log_file = cfg['log']['file']
    if log_path == None or log_file == None:
        print ('"logger.py": Failed to get log path+file from config file')
        sys.exit()
    else:
        log_path = log_path + log_file

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
    """
    # save info about a transaction
    @classmethod
    def transaction(cls, trans_id):
        # TODO: retrieve transaction info and write it to database
        cls.write('"log.py" in transaction(): Saving transaction info to database. ID: ', trans_id)
    """



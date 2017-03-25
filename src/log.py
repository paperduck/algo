#!/usr/bin/python3

"""
File:               log.py
Python version:     3.4
Description:        Class for writing to a log file.
How to use:
    Import the class from the module and call the static (class) methods.
    The location of the log file is specified in the non-public config file.
Remarks
    Sensitive information may be written to the log file, so keep it safe.
    Important stuff should be saved to the database because that makes it
    easier to analyze later.
    The log file should only be used for debugging.
"""

#*************************
import configparser
import datetime
#*************************
#*************************


class Log():

    cfg = configparser.ConfigParser()
    cfg.read('config_nonsecure.cfg')
    config_path = cfg['config_secure']['path']
    cfg.read(config_path)
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



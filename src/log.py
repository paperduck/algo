"""
File:               log.py
Python version:     3.4
Description:        Class for writing to a log file.
How to use:
    Import the class from the module and call `write()`.
    The location of the log file is specified in a config file.
Remarks
    Sensitive information may be written to the log file, so keep it safe.
    Important stuff should be saved to the database because that makes it
    easier to analyze later.
    The log file should only be used for debugging.
"""

#*************************
import datetime
#*************************
from config import Config
#*************************

class Log():

    log_file = open(Config.log_path, 'w')
    log_file.write('"log.py" __del__(): Log file opened.')
    
    @classmethod
    def __del__(cls):
        cls.log_file.close()
        cls.write('"log.py" __del__(): Log file closed.')
        

    @classmethod
    def clear(cls):
        """
        clear log
        """
        cls.write('')


    @classmethod
    def write(cls, *args):
        """
        append to log
        """
        dt = datetime.datetime.now().strftime("%c")
        msg = '\n' + dt + ':  '
        for a in list(args):
            msg = msg + str(a)
        cls.log_file.write(msg)


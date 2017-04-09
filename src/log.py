"""
File:               log.py
Python version:     3.4
Description:        Class for writing to a log file.
How to use:
    Import the class from the module and call `write()`.
    The location of the log file is specified in a config file.
    Initialization is automatic, but the log file must be closed manually
    by calling `shutdown()`.
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
    """
    The file is opened and closed every call to write() to flush the
    data and make the file watchable.
    """

    @classmethod
    def clear(cls):
        """
        clear log
        """
        with open(Config.log_path, 'w') as f:
            f.write('')
            f.close()


    @classmethod
    def write(cls, *args):
        """
        append to log
        """
        dt = datetime.datetime.now().strftime("%c")
        msg = '\n' + dt + ':  '
        for a in list(args):
            msg = msg + str(a)
        with open(Config.log_path, 'a') as f:
            f.write(msg)
            f.close


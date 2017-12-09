"""
File:               db.py
Python version:     3.4
Description:        database
"""

#*************************
import atexit
import collections
import concurrent.futures
import configparser
from datetime import datetime
import mysql.connector
from mysql.connector import errorcode, errors
from threading import Thread
import timeit
#*************************
from config import Config
from log import Log
#*************************

class DB():
    config = {
        'user': Config.db_user,
        'password': Config.db_pw,
        'host': Config.db_host,
        'database': Config.db_name
    }
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()


    """
    """
    @classmethod
    def shutdown(cls):
        try:
            cls.cursor.close()
        except:
            pass
        try:
            cls.cnx.close()
        except:
            pass


    """
    Return type:
        MySQL returns record sets as a list of tuples.
    """
    @classmethod
    def execute(
        cls,
        cmd     # string
    ):
        cls.cursor.execute(cmd)

        try:
            cls.cnx.commit()
        except mysql.connector.errors.InternalError:
            pass

        try:
            result = cls.cursor.fetchall()
        except errors.InterfaceError:
            return []
        else:
            return result


    """
    Report a bug.
    Parameter 'bug' is a string.
    """
    @classmethod
    def bug(cls, bug):
        cls.execute('INSERT INTO bugs (timestamp, description) values (NOW(), \'{}\')'
            .format(bug))


# There are not destructors in Python, so use this.
atexit.register(DB.shutdown)

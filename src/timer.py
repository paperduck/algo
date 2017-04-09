"""
Description:
    Convenient class for timing blocks of code.
    Intended to be used to time functions.

Overview:
    When class is created, it reads existing times from the db.
    Call the start() method to get the starting timestamp.
    Call the stop() method to stop timing and doesn't return anything of note.
    The stop method takes in some details including a unique identifier.
    The stop method checks to see if the duration is a new max, and
    automatically saves
"""

####################
import concurrent.futures
import datetime
import mysql.connector
from threading import Thread
import timeit
####################
from config import Config
from log import Log
import sys
####################


def timer_decorator(cls):
    # Load records from database, after the class is created.
    cls.records = cls._db_execute('SELECT * FROM function_times')
    if cls.records == None:
        Log.write('records == None. Aborting.')
        sys.exit()
    print('"timer.py" timer_decorator(): cls.records is initialized to {}'.format(cls.records))
    return cls
    

@timer_decorator
class Timer():

    """
    The db module is not used because that would create a circular
    dependence; the db module uses this module to time itself.
    """
    db_config = {
        'user': Config.db_user,
        'password': Config.db_pw,
        'host': Config.db_host,
        'database': Config.db_name
    }
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    """
    "Records" as in breaking a record; new max duration.
    The records variable is a list of dicts that matches the table columns:
        function_name (PK)
        timestamp
        duration
        note
    """
    records = [] # TODO Use hash table for fast insertion.


    @classmethod
    def _db_execute(cls, cmd):
        def execute(cmd):
            cls.cursor.execute(cmd)
            try:
                cls.cnx.commit()
            except mysql.connector.errors.InternalError:
                pass
            try:
                return cls.cursor.fetchall()
            except mysql.connector.errors.InterfaceError:
                return []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(execute, cmd)
            return future.result()


    @classmethod
    def start(cls):
        return timeit.default_timer()


    @classmethod
    def stop(cls, start, function_name, note):
        """
        Compare a new time to the record.
        If the new time is a record, save it.
        """
        Log.write('"timer.py" stop(): Entering with records:\n',
            '{}'.format(cls.records))
        timestamp = datetime.datetime.now()
        duration = timeit.default_timer() - start
        new_max = False
        found = False
        for r in cls.records:
            r_fun = r[0]
            r_time = r[1]
            r_dur = r[2]
            r_note = r[3]
            if r_fun == function_name:
                Log.write('"timer.py" stop(): Function {} has previous max duration of {}'
                    .format(
                        r_fun,
                        r_dur)
                    )
                found = True
                sec = int(duration)
                if datetime.timedelta(seconds=sec,microseconds=duration-sec) > r_dur:
                    # new max
                    new_max = True
                    r_dur = duration
                    r_note = note
                break # found it
        if not found:
            # create new entry
            new_max = True
            cls.records.append((timestamp,function_name, duration, note))
        # save to database if new max duration
        if new_max:
            Log.write('"timer.py" stop(): New max duration for ',
                'function {} = {}s'.format(function_name, duration))
            db_result = cls._db_execute(
                'INSERT INTO function_times \
                (function_name, timestamp, duration, note) \
                VALUES ("{0}","{1}","{2}","{3}") \
                ON DUPLICATE KEY UPDATE \
                timestamp="{1}", \
                duration="{2}", \
                note="{3}"'
                .format(
                    function_name,
                    timestamp,
                    duration,
                    note
                )
            )
        else:
            Log.write('"timer.py" stop(): Not a new duration: {} for function {}'
                .format(duration, function_name))

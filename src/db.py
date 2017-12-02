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
from timer import Timer
#*************************

def db_decorator(cls):
    """
    Runs after class is created.
    Need the class to be created first.
    """
    # Start the worker thread. 
    worker_thread = Thread(target=cls._work).start()
    return cls


@db_decorator
class DB():
    """
    Two queues (jobs and results) because only having one queue for both
    necessitates locking the queue to prevent its size from changing; the
    worker needs to access the end item via index, which might change
    if new tasks are popped.
    
    @classmethod is used instead of @staticmethod because the functions need
    to share data.
    """
    config = {
        'user': Config.db_user,
        'password': Config.db_pw,
        'host': Config.db_host,
        'database': Config.db_name
    }
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    jobs = collections.deque() # TODO: Originally needed a deque, but queue is fine now
    results = [] #TODO make this a heap for fast deletion
    next_job_id = 0
    halt = False
    worker_thread = None


    @classmethod
    def shutdown(cls):
        """
        Clean up connections, threads, etc.
        atexit() will call this, but you should call this anyway.
        """
        cls.halt = True
        #while (len(cls.jobs) > 0):
        #    Log.write('"db.py" shutdown(): waiting for queue to empty')
        if cls.worker_thread != None:
            worker_thread.join() # block until worker thread finishes
        try:
            cls.cursor.close()
        except:
            pass
        try:
            cls.cnx.close()
        except:
            pass


    """
    Return type: void
    """
    @classmethod
    def _work(cls):
        """
        Main loop for worker thread.
        Do work until halted, then finish up the queue.
        """
        try:
            while (not cls.halt):
                cls._work_body()
        except KeyboardInterrupt:
            Log.write('"db.py" _work(): ',
                'KeyboardInterrupt. Finishing remaining jobs...')
            while (len(cls.jobs) > 0):
                cls._work_body()
        else:
            Log.write('"db.py" _work(): Halted. Finishing jobs...')
            while (len(cls.jobs) > 0):
                cls._work_body()


    """
    Return type: void
    """
    @classmethod
    def _work_body(cls):
        """
        Execute the command at the end of the queue.
        Store the result in the results pool.
        """
        start = Timer.start()
        #job = None
        try:
            job = cls.jobs.pop()
        except IndexError:
            # queue is empty
            return
        Log.write('"db.py" _work_body(): Executing: \n{}'.format(job[1]))
        cls.cursor.execute(job[1])
        """
        commit() only needs to be called for transactions that modify
        data. TODO: Do this in a cleaner way.
        https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-commit.html
        """
        try:
            cls.cnx.commit()
        except mysql.connector.errors.InternalError:
            pass
        """
        "You must fetch all rows for the current query before executing new
        statements using the same connection."
        https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-fetchall.html
        """
        try:
            result = cls.cursor.fetchall()
        except errors.InterfaceError:
            cls.results.append((job[0], []))
        else:
            cls.results.append((job[0], result))
        Timer.stop(start, 'DB._work_body', job[1])
            

    """
    Return type:
        None if halted
        MySQL returns record sets as a list of tuples.
    Description:
        Add a task to the queue, then wait for the result.
        _put() adds the job to the queue and returns the job_id.
        _get() scans the result pool for that job_id, returns the result.
    """
    @classmethod
    def execute(cls, cmd):
        if (cls.halt):
            return None
        job_id = cls._put(cmd)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_result = executor.submit(cls._get, job_id)
            return future_result.result()


    """
    Report a bug.
    Parameter 'bug' is a string.
    """
    @classmethod
    def bug(cls, bug):
        cls.execute('INSERT INTO bugs (timestamp, description) values (NOW(), \'{}\')'
            .format(bug))


    """
    Return type: void
    Job queue is tuples: (job ID, cmd string to send to database)
    """
    @classmethod
    def _put(cls, cmd):
        if (cls.halt):
            return
        job_id = cls._generate_job_id()
        cls.jobs.append((job_id, cmd))
        return job_id


    """
    Return type: List of tuples (MySQL Python API).
    Return value: Result set returned by database call.
    Scan the results pool until the result is found.
    Results pool is list of tuples: (job ID, result)
    """
    @classmethod
    def _get(cls, job_id):
        while True:
            num_results = len(cls.results)
            if num_results > 0:
                for index in range(0, num_results):
                    if cls.results[index][0] == job_id:
                        result = cls.results.pop(index)
                        return result[1] # TODO: fix thread return system
   
 
    @classmethod
    def _generate_job_id(cls):
        if cls.next_job_id >= 10000: # TODO: set max size on queues
            cls.next_job_id = 0
        cls.next_job_id = cls.next_job_id + 1
        return cls.next_job_id - 1 


# There are not destructors in Python, so use this.
atexit.register(DB.shutdown)

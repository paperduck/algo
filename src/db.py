#!/usr/bin/python3

"""
File:               db.py
Python version:     3.4
Description:        db layer
    Two queues (jobs and results) because only having one queue for both
    necessitates locking the queue to prevent its size from changing; the
    worker needs to access the end item via index, which might change
    if new tasks are popped.
"""

#*************************
import collections
import configparser
import mysql.connector
from mysql.connector import errorcode, errors
#import queue
from threading import Thread
#*************************
from log import Log
#*************************


def worker_decorator(cls):
    """
    Runs after class is created.
    Decorator because need the class to be created first.
    """
    # Start the worker thread. 
    cls.worker_thread = Thread(target=cls._work).start()
    return cls    


@worker_decorator
class DB():
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
    config = {
        'user': cfg['mysql']['username'],
        'password': cfg['mysql']['password'],
        'host': cfg['mysql']['host'],
        'database': cfg['mysql']['database']
    }
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    jobs = collections.deque()
    results = [] #TODO make this a heap for fast deletion
    next_job_id = 0
    halt = False


    @classmethod
    def shutdown(cls):
        cls.halt = True
        while (len(cls.jobs) > 0):
            Log.write('"db.py" shutdown(): waiting for queue to empty')
        cls.cursor.close()
        cls.cnx.close()


    @classmethod
    def _work(cls):
        """
        Execute the command at the end of the queue.
        Replace the command with its result so _put_get() can retrive the
        result.

        "You must fetch all rows for the current query before executing new
        statements using the same connection."
        https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-fetchall.html
        """
        while (not cls.halt):
            cls._work_body()
        # finish the queue before halting
        while (len(cls.jobs) > 0):
            cls._work_body()


    @classmethod
    def _work_body(cls):
        #job = None
        try:
            job = cls.jobs.pop()
        except IndexError:
            return
        cls.cursor.execute(job[1])
        cls.cnx.commit()
        try:
            result = cls.cursor.fetchall()
        except errors.InterfaceError:
            cls.results.append((job[0], []))
        else:
            cls.results.append((job[0], result))
            

    @classmethod
    def execute(cls, cmd):
        """
        _put() adds the job to the queue and returns the job_id
        _get() scans the result pool for that job_id, returns the result
        """
        return Thread(target=cls._get, args=(cls._put(cmd),)).start()


    @classmethod
    def _put(cls, cmd):
        """
        Job queue is tuples: (job ID, cmd string to send to database)
        """
        job_id = cls.generate_job_id()
        cls.jobs.append((job_id, cmd))
        return job_id


    @classmethod
    def _get(cls, job_id):
        """
        Scan the results pool until the result is found.
        Results pool is tuples: (job ID, result)
        Returns: Whatever the database call returns, e.g. the result set of
        a query.
        """
        while True:
            for index in range(0, len(cls.results)):
                if cls.results[index][0] == job_id:
                    return cls.results.pop(index)[1]

    
    @classmethod
    def generate_job_id(cls):
        if cls.next_job_id >= 10000: # TODO: set max size on queues
            cls.next_job_id = 0
        cls.next_job_id = cls.next_job_id + 1
        return cls.next_job_id - 1 


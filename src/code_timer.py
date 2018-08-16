import datetime
import timeit

class CodeTimer():

    @classmethod
    def start(cls):
        """ Returns the wall clock time, in seconds """
        return timeit.default_timer()


    @classmethod
    def stop(cls, start):
        """ Returns the duration of time passed, in seconds.
        
        Parameters:
            start: float - return value of start()
        """
        duration = timeit.default_timer() - start
        if duration < 0:
            duration += 60*60*24
        return duration

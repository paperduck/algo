#!/usr/bin/python 

"""
File:           opportunities.py
Python verion:  3.4
Description:
    The `opportunity` class represents one order.
    The `opportunities` class is a list of opportunities.
"""


#*************************
#*************************
from log import *
from order import *
#*************************


class Opportunity():
    """
    """

    def __init__(self):
        """
        """
        """
        type: int 1-100
        description: estimated rating of success
        """
        self.confidence = 1
        """
        type: string
        description: ID (name) of strategy
        """
        self.strategy = None
        """
        type: order
        description: Produce an order object that can be passed to `Broker`
        """
        self.order = None # TODO
        """
        """
        self.reason = ''

    def __str__(self):
        """
        """
        return 'opportunity'

    
class Opportunities():
    """
    """

    def __init__(self):
        """
        """
        self._opportunities = []


    def __str__(self):
        """
        """
        return 'opportunities'


    def clear(self):
        self._opporunities = []


    def push(self, opp):
        """
        Take an opportunity dict and add it to the list.
        """
        self._opportunities.append(opp)


    def pick(self, instrument=None):
        """
        Find and return the best opportunity. If you want more than one,
        just call this repeatedly.

        TODO: use the instrument parameter to restrict which opp to pop.
        """
        # Just pick the one with the highest confidence rating.
        if self._opportunities == []:
            return None
        max_conf_index = 0
        max_conf = 0
        for i in range(0, len(self._opportunities) - 1):
            if self._opportunities[i]['confidence'] > max_conf:
                max_conf_index = i
        return self._opportunities.pop(max_conf_index)



#!/usr/bin/python 

"""
File:           opportunities.py
Python verion:  3.4
Description:    The `opportunity` class represents one order.
    The `opportunities` class is a list of opportunities.
"""


#*************************
#*************************
from log import *
#*************************


class Opportunity():
    """
    """

    def __init__(self):
        """
        """
        # type: int 1-100
        # description: estimated rating of success
        self.confidence = 1
        # type: string
        # description: ID (name) of strategy
        self.strategy = None
        # type: <order object>
        # description: Order object that can be passed to broker API
        self.order = None

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
        self.opportunities = []

    def __str__(self):
        """
        """
        return 'opportunities'

    def push(self, opp):
        """
        Take an opportunity dict and add it to the list.
        """
        self.opportunities.append(opp)

    def pop (self, instrument=None):
        """
        Find and return the best opportunity.
        If there are no opportunities, return an empty dict.
        If an error occurs, return None.
        TODO: use the instrument parameter to restrict which opp to pop.
        """
        # Just pick the one with the highest confidence rating.
        max_conf_index = -1
        max_conf = 0
        if self.opportunities == []:
            return {}
        for i in range(0, len(self.opportunities) - 1):
            if self.opportunities[i]['confidence'] > max_conf:
                max_conf_index = i
        return self.opportunities.pop(max_conf_index)
        




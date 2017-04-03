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
from log import Log
from order import Order
#*************************


class Opportunity():
    """
    """

    def __init__(self):
        """
        Description: The <Order> instance to be set by a strategy when it suggests
        an opportunity.
        Type: <Order>
        """
        self.order = None
        """
        description: estimated rating of success
        type: Int 1-100
        """
        self.confidence = 1
        """
        Description:
            Reference to strategy class that created this opportunity.
            <Trade> objects also hold a reference to their strategy.
        Type: <Strategy>
        """
        self.strategy = None
        """
        A note to save to the database.
        Type: String
        """
        self.reason = ''

    def __str__(self):
        """
        """
        return 'Opportunity:\norder: {}\nconfidence: {}\nstrategy: {}\nreason: {}\n\
            '.format(self.order, self.confidence, self.strategy.get_name(), self.reason)


class Opportunities():
    """
    """

    def __init__(self):
        """
        List of <Opportunity>.
        """
        self._opportunities = []


    def __str__(self):
        """
        """
        return 'Opportunities'


    def clear(self):
        self._opporunities = []


    def push(self, opp):
        """
        Add an <Opportunity> to the list.
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



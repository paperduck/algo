# File: entrance.py
# Python 3.4

# List of opportunities to enter a trade.
# Limitations such as which instruments to use and number of units
#   are managed by whatever uses this module. 
#   This is simply a list. The contents of the list do not matter here.

import log

# TODO: Put processor-heavy strategies into their own thread or processor core. 

class entrance():
    
    #
    def __init__(self):
        # sorted list of dictionaries. Each dict is an entrance opportunty.
        self.opportunities = []

        # mutex
        self.locked = False


    # Return index of opp with highest favorability.
    def _get_best_opp_index(self):
        max_fav_index = -1
        max_fav = 0
        for i in range(0, len(self._opportunities) - 1):
            if self._opportunities[i]['fav'] > max_fav:
                max_fav_index = i
        if max_fav_index == -1:
            return None
        else:
            return max_fav_index

    # Select best opportunity. Take current positions into account.
    # Returns:
    #   Dictionary containing information about an order that should be placed.
    #   Dict must contain parameters to place an order through Oanda's API.
    # If an error occurs, return some information about that error.
    def pop_opportunity(self, instrument):
        if self.in_use:
            algo_log.write_to_log('in entrance.pop_opportunity(): Locked. Returning None.')
            self.in_use = False
            return None
        else:
            # Make sure there are opportunities
            if len(self._opportunities) < 1:
                self.in_use = False
                return None
            else: 
                opp = self._opportunities.pop( self._get_best_opp_index() )
                self.in_use = False
                return opp
        
    # mutex
    def is_locked(self):
        return self.locked
    def lock(self):
        self.locked = True




class Instrument():
    
    """
    Return value: void
    """
    def __init__(self, new_id, name):
        # db key; internal to this application
        self._id = new_id   # string
        # from db, but also standard industry symbol
        self._name = name   # string


    """
    """
    def get_id(self):
        return self._id    


    """
    Return value: string
    The name as Oanda knows it.
    This should only be used in the Oanda translator module (oanda.py).
    """
    def get_name_oanda(self):
        return self._name

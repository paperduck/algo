
import atexit
from config import Config
from db import DB
from log import Log

class Instrument():
    
    #self._lookup_table = Instrument.lookup()


    """
    TODO: Load the instruments from database into memory for fast lookup.
    """
    def __init__(self, new_id):
        self._id = new_id      
        self._name = self.get_name_from_id(new_id)


    """
    Return type: string
    """
    def get_id(self):
        return self._id    


    """
    Return type: string
    Name as a string, depending on the broker being used.
    """
    def get_name(self):
        return self._name
    

    """
    Return type: int
    TODO: use the cache
    """
    @classmethod
    def get_id_from_name(cls, name):
        if Config.broker_name == 'oanda':
            result = DB.execute(
                'SELECT id FROM instruments WHERE oanda_name="{}"'.format(name))
            if len(result) != 1:
                Log.write('instrument.py get_id_from_name(): len(result) was {}'.format(len(result)))
                raise Exception
            return result[0][0]
        else:
            raise Exception


    """
    TODO: use the cache
    param:      type:
    id_key      int
    """
    @classmethod
    def get_name_from_id(cls, id_key):
        if Config.broker_name == 'oanda':
            result = DB.execute(
                'SELECT oanda_name FROM instruments WHERE id={}'.format(id_key))
            if len(result) != 1:
                Log.write('instrument.py get_name_from_id(): len(result) was {}'.format((len(result))))
                raise Exception 
            return result[0][0]
        else:
            raise Exception
    

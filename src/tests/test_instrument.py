"""
Test the instrument module.
"""

# library imports
import sys
import unittest
from unittest.mock import MagicMock, patch, call

# Need to modify sys.path because Python doesn't have relative imports.
# sys.path is initialized from environment variable PYTHONPATH.
try:
    sys.path.index('/home/user/raid/software_projects/algo/src')
except ValueError:
    sys.path.append('/home/user/raid/software_projects/algo/src')

# local imports
from config import Config
from db import DB
from instrument import Instrument

class TestInstrument(unittest.TestCase):

    I_ID = 4
    I_NAME = 'USD_JPY'
    TARGET_BROKER_NAME = 'oanda'


    # called for every test method
    def setUp(self):
        self.assertEqual(Config.broker_name, self.TARGET_BROKER_NAME)


    # called for every test method
    def tearDown(self):
        DB.shutdown() # this might cause trouble for multiple tests
        pass

    
    """
    """
    def test_1(self):
        instrument = Instrument(self.I_ID)
        self.assertEqual(instrument.get_id(), self.I_ID)
        self.assertEqual(instrument.get_name(), self.I_NAME)
        self.assertEqual(instrument.get_name_from_id(2), 'DCK')
        self.assertEqual(Instrument.get_id_from_name('SNK'), 3)


if __name__ == '__main__':
    unittest.main()


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

class TestStrategy(unittest.TestCase):

    # called for every test method
    def setUp(self):
        pass


    # called for every test method
    def tearDown(self):
        DB.shutdown() # this might cause trouble for multiple tests
        pass

    
    """
    """
    def test___str__(self):


    """
    """
    def test_get_name(self):


    """
    """
    def test_trade_opened(self):


    """
    """
    def test_trade_closed(self):


    """
    """
    def test_trade_reduced(self):


    """
    """
    def test_recover_trades(self):


    """
    """
    def test_drop_all(self):


    """
    """
    def test_refresh(self):


    """
    """
    def test__babysit(self):


    """
    """
    def test__scan(self):


if __name__ == '__main__':
    unittest.main()


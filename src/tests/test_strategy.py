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
from db import DB
from strategy import Strategy

class SampleStrategy(Strategy):
    def __init__(self):
        pass
    def get_name(self):
        return 'sample'
    def _babysit(self):
        pass
    def _scan(self):
        return None

class TestStrategy(unittest.TestCase):

    _strat = SampleStrategy()

    # called for every test method
    def setUp(self):
        pass


    # called for every test method
    def tearDown(self):
        pass

    
    def test___str__(self):
        self.assertEqual(str(self._strat.get_name()), 'sample')


    def test_get_name(self):
        self.assertEqual(self._strat.get_name(), 'sample')


    def test_trade_opened(self):
        """
        TODO: check db too
        """
        #import pdb; pdb.set_trace()
        self._strat.open_trade_ids = []
        self._strat.trade_opened('1')
        self.assertEqual(self._strat.open_trade_ids, ['1'])
        self._strat.trade_opened('666')
        self.assertEqual(self._strat.open_trade_ids, ['1','666'])
        self._strat.trade_opened('mx.!@#$%^&*()_+=-/|')
        self.assertEqual(self._strat.open_trade_ids, ['1','666','mx.!@#$%^&*()_+=-/|'])
        DB.execute("DELETE FROM open_trades_live WHERE trade_id in ('1', '666', 'mx.!@#$%^&*()_+=-/|')")


    def test_recover_trades(self):
        pass


    def test_drop_all(self):
        pass


    def test_refresh(self):
        pass


    def test__babysit(self):
        pass


    def test__scan(self):
        pass


if __name__ == '__main__':
    unittest.main()

import atexit
atexit.register(DB.shutdown)

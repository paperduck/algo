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
    @classmethod
    def get_name(cls):
        return 'sample'
    @classmethod
    def _babysit(cls):
        pass
    @classmethod
    def _scan(cls):
        return None

class TestStrategy(unittest.TestCase):

    # called for every test method
    def setUp(self):
        pass


    # called for every test method
    def tearDown(self):
        pass

    
    """
    """
    def test___str__(self):
        self.assertEqual(str(SampleStrategy.get_name()), 'sample')


    """
    """
    def test_get_name(self):
        self.assertEqual(SampleStrategy.get_name(), 'sample')


    """
    TODO: check db too
    """
    def test_trade_opened(self):
        #import pdb; pdb.set_trace()
        SampleStrategy._open_trade_ids = []
        SampleStrategy.trade_opened('1')
        self.assertEqual(SampleStrategy._open_trade_ids, ['1'])
        SampleStrategy.trade_opened('666')
        self.assertEqual(SampleStrategy._open_trade_ids, ['1','666'])
        SampleStrategy.trade_opened('mx.!@#$%^&*()_+=-/|')
        self.assertEqual(SampleStrategy._open_trade_ids, ['1','666','mx.!@#$%^&*()_+=-/|'])
        DB.execute("DELETE FROM open_trades_live WHERE trade_id in ('1', '666', 'mx.!@#$%^&*()_+=-/|')")


    """
    """
    def test_trade_closed(self):

        # try to delete from empty list
        SampleStrategy._open_trade_ids = []
        self.assertRaises(Exception, SampleStrategy.trade_closed, '1')

        # try to delete from non-empty list, but trade not found in list.
        SampleStrategy._open_trade_ids = ['1','2','3']
        self.assertRaises(Exception, SampleStrategy.trade_closed, '4')

        # try to delete from list (normal/success)
        SampleStrategy._open_trade_ids = ['1','2','3']
        SampleStrategy.trade_closed('2')
        self.assertEqual(SampleStrategy._open_trade_ids, ['1','3'])
        SampleStrategy.trade_closed('3')
        self.assertEqual(SampleStrategy._open_trade_ids, ['1'])
        SampleStrategy.trade_closed('1')
        self.assertEqual(SampleStrategy._open_trade_ids, [])



    """
    """
    def test_trade_reduced(self):
        pass


    """
    """
    def test_recover_trades(self):
        pass


    """
    """
    def test_drop_all(self):
        pass


    """
    """
    def test_refresh(self):
        pass


    """
    """
    def test__babysit(self):
        pass


    """
    """
    def test__scan(self):
        pass


if __name__ == '__main__':
    unittest.main()

import atexit
atexit.register(DB.shutdown)

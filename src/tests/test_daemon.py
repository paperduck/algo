"""
Run like so:
    $ python3 tests.py

The daemon is assumed to only use the Fifty strategy module.
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

# Have to mock db.DB before daemon.py (etc.) imports it.
#real_db = DB
#real_db_execute = DB.execute
sys.modules['db'] = MagicMock()
from db import DB

# project imports
from daemon import Daemon
from instrument import Instrument
from strategies.fifty import Fifty
from trade import TradeClosedReason, Trade, Trades

class TestDaemon(unittest.TestCase):

    _NAME = 'TestDaemon'

    # called for every test method
    def setUp(self):
        pass


    # called for every test method
    def tearDown(self):
        pass

    """
    Test: Daemon.recover_trades()
    Scenarios:
        - No trades in broker or db
            Assertions:
                - Strategies recover no trades
        - Trade in broker and db
            Assertions:
                - Trade gets distributed to correct strategy
        - Trade is in broker, not db
            Assert:
                - Trade deleted from db
                - Trade gets distributed to correct strategy
        - Trade in db, broker unsure
            Assert:
                - Trade deleted from db
                - Trade's strategy does NOT adopt it
        - Trade in db has wonky data (non-existant strategy name, etc.)
        - (All):
            Assert: trades are distributed to strategies.
    """
    @patch('daemon.Broker')
    def test_recover_trades(self, mock_broker):
        #print(self._NAME + '.test_recover_trades')

        """
        Scenario: No trades in broker or db
        """
        mock_broker.get_trades = MagicMock(return_value=Trades())
        DB.execute.return_value = []

        Daemon.recover_trades()
        # Check that no trades were adopted
        for s in Daemon.strategies:
            self.assertEqual(len(s._open_trade_ids), 0)

        """
        Scenario: Trade in broker and db
        """
        def db_execute(query):
            if query == 'SELECT trade_id FROM open_trades_live':
                return [('id666',)]
            elif query == 'SELECT strategy, broker FROM open_trades_live WHERE trade_id="id666"':
                return [('Fifty', 'oanda')]        
            elif query == 'SELECT oanda_name FROM instruments WHERE id=4':
                return [('USD_JPY',)]
            else:
                print('unexpected query: {}'.format(query))
                raise Exception
        DB.execute = db_execute
        trades = Trades()
        trades.append(Trade(
            broker_name='oanda',
            instrument=Instrument(4),
            go_long=True, stop_loss=90, strategy=Fifty, take_profit=100,
            trade_id='id666'
        ))
        mock_broker.get_trades = MagicMock(return_value=trades)
        
        Daemon.recover_trades()
        # check Fifty adopted one trade
        for s in Daemon.strategies:
            if s.get_name() == 'Fifty':
                self.assertEqual(len(s._open_trade_ids), 1)
            else:
                self.assertEqual(len(s._open_trade_ids), 0)
        # check trade is the trade we think it is
        self.assertEqual(Fifty._open_trade_ids[0], 'id666')
        '''
        self.assertEqual(Fifty._open_trades[0].get_broker_name(), 'oanda')
        self.assertEqual(Fifty._open_trades[0].get_instrument().get_name(), 'USD_JPY')
        self.assertEqual(Fifty._open_trades[0].get_instrument().get_id(), 4)
        self.assertEqual(Fifty._open_trades[0].get_go_long(), True)
        self.assertEqual(Fifty._open_trades[0].get_stop_loss(), 90)
        self.assertEqual(Fifty._open_trades[0].get_take_profit(), 100)
        self.assertEqual(Fifty._open_trades[0].get_trade_id(), 'id666')
        '''
        # Cleanup
        Fifty.drop_all()

        """
        Scenario: Trade is in broker, not db
        """
        # Trade may have been opened manually.
        # Nothing should happen for these trades.
        def db_execute(query):
            if query == 'SELECT trade_id FROM open_trades_live':
                return []
            elif query == 'SELECT strategy, broker FROM open_trades_live WHERE trade_id="id666"':
                return []        
            elif query == 'SELECT oanda_name FROM instruments WHERE id=4':
                return [('USD_JPY',)]
            else:
                raise Exception
        DB.execute = MagicMock(side_effect=db_execute)
        trades = Trades()
        trades.append(Trade(
            broker_name='oanda',
            instrument=Instrument(4),
            go_long=True, stop_loss=90, strategy=Fifty, take_profit=100,
            trade_id='id666'))
        mock_broker.get_trades = MagicMock(return_value=trades)

        Daemon.recover_trades()
        # db should stay the same (no inserts or deletions)
        # Broker trades should stay the same...
        calls = [
            call('SELECT trade_id FROM open_trades_live'),
            call('SELECT strategy, broker FROM open_trades_live WHERE trade_id="id666"')
        ]
        DB.execute.assert_has_calls(calls)
        # Check no trades adopted
        for s in Daemon.strategies:
            self.assertEqual(len(s._open_trade_ids), 0)
 
        """
        Scenario: Trade in db, broker unsure
        """
        def db_execute(query):
            if query == 'SELECT trade_id FROM open_trades_live':
                return [('id666',)]
            elif query == 'SELECT strategy, broker FROM open_trades_live WHERE trade_id="id666"':
                return [('Fifty', 'oanda')]        
            elif query == 'SELECT oanda_name FROM instruments WHERE id=4':
                return [('USD_JPY',)]
            elif query == 'DELETE FROM open_trades_live WHERE trade_id="id666"':
                return
            else:
                raise Exception
        DB.execute = MagicMock(side_effect=db_execute)
        mock_broker.get_trades = MagicMock(return_value=Trades())
        
        Daemon.recover_trades()
        # Check trade deleted from db
        calls = [
            call('SELECT trade_id FROM open_trades_live'),
            call('DELETE FROM open_trades_live WHERE trade_id="id666"')        
        ]
        DB.execute.assert_has_calls(calls)
        # Check no trades adopted
        for s in Daemon.strategies:
            self.assertEqual(len(s._open_trade_ids), 0)

        """ 
        module cleanup
        """
        Daemon.shutdown()

if __name__ == '__main__':
    unittest.main()

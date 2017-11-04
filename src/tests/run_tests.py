"""
Run like so:
    $ python3 run_tests.py
"""

import os
import unittest
from unittest import mock
from unittest.mock import patch

os.chdir('/home/user/raid/software_projects/algo/src/')
def test_all():

    import test_daemon
    #import test_db
    #import test_oanda

    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_daemon))
    #suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_db))
    #suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_oanda))
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    test_all()


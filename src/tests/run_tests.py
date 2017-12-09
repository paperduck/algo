"""
Don't use this.
Some tests mock modules, which is difficult to unwind.
Instead, use the bash script so that the Python environment completely
shuts down between tests, thereby resetting the mocked modules.
"""

import os
import unittest
from unittest import mock
from unittest.mock import patch
import sys

# Need this to import local modules
os.chdir('/home/user/raid/software_projects/algo/src/')


def test_all():

    suite = unittest.TestSuite()

    from test_daemon import TestDaemon
    import test_instrument

    #suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_daemon))
    #suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_instrument))

    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    test_all()


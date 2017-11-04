"""
Run like so:
    $ python3 tests.py
"""

import unittest

class TestDaemon(unittest.TestCase):

    def setUp(self):
        # called for every test method
        pass

    def tearDown(self):
        # called for every test method
        pass
    
    def test_1(self):
        self.assertEqual(1, True)

if __name__ == '__main__':
    unittest.main()


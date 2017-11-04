"""
Run like so:
    $ python3 tests.py
"""

import unittest

class TestDaemon(unittest.TestCase):

    def setUp(self):
        # called for every test method
        print('set up')

    def tearDown(self):
        # called for every test method
        print('tear down')
    
    def test_1(self):
        print('test_1')
        self.assertEqual(1, True)

    def test_2(self):
        print('test_2')
        self.assertEqual(1, True)

if __name__ == '__main__':
    unittest.main()


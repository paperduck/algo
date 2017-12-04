"""
Test the util_date module.
"""

# library imports
import datetime
import sys
import unittest

# Need to modify sys.path because Python doesn't have relative imports.
# sys.path is initialized from environment variable PYTHONPATH.
try:
    sys.path.index('/home/user/raid/software_projects/algo/src')
except ValueError:
    sys.path.append('/home/user/raid/software_projects/algo/src')

# local imports
import util_date

class TestInstrument(unittest.TestCase):

    # called for every test method
    def setUp(self):
        pass

    # called for every test method
    def tearDown(self):
        pass

    
    """
    """
    def test_string_to_date(self):
        # normal numbers
        sample_string = '2014-07-02T04:14:59.123456Z'
        target_date = datetime.datetime(
            year=2014, month=7, day=2, hour=4,
            minute=14, second=59, microsecond=123456) 
        result_date = util_date.string_to_date(sample_string)
        self.assertEqual(target_date, result_date)
        
        # minimum
        sample_string = '0001-01-01T00:00:00.000000Z'
        target_date = datetime.datetime(
            year=datetime.MINYEAR, month=1, day=1, hour=0,
            minute=0, second=0, microsecond=0) 
        result_date = util_date.string_to_date(sample_string)
        self.assertEqual(target_date, result_date)

        # maximum
        sample_string = '9999-12-31T23:59:59.999999Z'
        target_date = datetime.datetime(
            year=datetime.MAXYEAR, month=12, day=31, hour=23,
            minute=59, second=59, microsecond=999999) 
        result_date = util_date.string_to_date(sample_string)
        self.assertEqual(target_date, result_date)

    """
    """
    def test_date_to_string(self):
        # normal numbers
        sample_date = datetime.datetime(
            year=2014, month=7, day=2, hour=4,
            minute=14, second=59, microsecond=123456) 
        target_string = '2014-07-02T04:14:59.123456Z'
        result_string = util_date.date_to_string(sample_date)
        self.assertEqual(target_string, result_string)

        # minimum - I'm not sure if brokers would want years to be zero padded.
        sample_date = datetime.datetime(
            year=1950, month=1, day=1, hour=0,
            minute=0, second=0, microsecond=0) 
        target_string = '1950-01-01T00:00:00.000000Z'
        result_string = util_date.date_to_string(sample_date)
        self.assertEqual(target_string, result_string)

        # maximum
        sample_date = datetime.datetime(
            year=datetime.MAXYEAR, month=12, day=31, hour=23,
            minute=59, second=59, microsecond=999999) 
        target_string = '9999-12-31T23:59:59.999999Z'
        result_string = util_date.date_to_string(sample_date)
        self.assertEqual(target_string, result_string)



if __name__ == '__main__':
    unittest.main()


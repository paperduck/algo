"""
Date utilities
"""

from datetime import datetime
from log import Log


"""
Day of week enumeration.
Matches ISO weekday numbers.
"""
MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
SUNDAY = 7


def date_to_string(d):
    """Returns: string
    Convert datetime to string in RFC3339 format:
    "YYYY-MM-DDTHH:MM:SS.MMMMMMMMMZ"
    param:  type:
        d   datetime in UTC
    """
    try:
        # strftime %f formats to 6 digit ms, but Oanda uses 9.
        six_digit_milliseconds = datetime.strftime(d, '%Y-%m-%dT%H:%M:%S.%f')
        nine_digit_milliseconds = six_digit_milliseconds[0:26] + '000Z'
        return nine_digit_milliseconds
    except:
        Log.write(
            'util_date.py date_to_string(): Failed to convert date({}) to string.'
            .format(d))
        raise Exception


def string_to_date(s):
    """Return type: datetime
    Parse a string into a datetime.
    param:  type:
        s   String of UTC datetime.
            Oanda typically sends 9-digit milliseconds with a Z on the end.
            Six digits of milliseconds are preserved by Python's datetime.
    """
    try:
        #z_index = s.rfind('Z')
        dot_index = s.rfind('.')
        return datetime.strptime(s[0:dot_index + 7], '%Y-%m-%dT%H:%M:%S.%f')
    except:
        Log.write(
            'util_date.py string_to_date(): Failed to convert string ({}) to date.'
            .format(s))
        raise Exception


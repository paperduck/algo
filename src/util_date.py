"""
Date utilities
"""

from datetime import datetime, timezone
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


''' problems with float limitations
def datetime_to_numeric(dt):
    """Return type: float
    Datetime to UTC numeric representation in this format:
    YYYYMMDDHHMMSS.<milliseconds...>
    """
    dt_utc = dt.replace(tzinfo=timezone.utc)
    print('\n dt_utc = {} \n'.format(dt_utc) )
    try:
        dt_string = dt_utc.strftime( '%Y%m%d%H%M%S.%f' ) 
        print('\n dt_string = {} \n'.format(dt_string) )
    except:
        Log.write('util_date.py datetime_to_numeric(): Failed to convert to string')
        raise Exception
    try:
        print('\n float(dt_string) = {} \n'.format( float(dt_string) ) )
        return float(dt_string)
    except:
        Log.write('util_date.py datetime_to_numeric(): Failed to convert to numeric')
        raise Exception
'''

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


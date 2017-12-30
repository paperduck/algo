"""
Date utilities
"""

import datetime


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


"""
Return type: string
Returns date in this format: "YYYY-MM-DDTHH:MM:SS.MMMMMMZ"
where the Z is an actual Z.
param:  type:
    d   datetime in UTC
"""
def date_to_string(d):
    try:
        return datetime.datetime.strftime(d, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        return None


"""
Return type: datetime or None
"YYYY-MM-DDTHH:MM:SS.MMMMMMZ"
Timestamp is assumed to be a UTC time.
Returns a datetime type.
param:  type:
    s   string
"""
def string_to_date(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        return None


"""
Date utilities
"""

import datetime


"""
Return type: string
Returns date in this format: "YYYY-MM-DDTHH:MM:SS.MMMMMMZ"
where the Z is an actual Z.
param:  type:
    d   datetime in UTC
"""
def date_to_string(d):
    return datetime.strftime(d, '%Y-%m-%dT%H:%M:%S.%fZ')


"""
Return type: datetime
"YYYY-MM-DDTHH:MM:SS.MMMMMMZ"
Timestamp is assumed to be a UTC time.
Returns a datetime type.
param:  type:
    s   string
"""
def string_to_date(s):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')



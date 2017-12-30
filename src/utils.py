""" 
Utilities
"""

import urllib


"""
Return type: string
Converts a list of <Instrument> instances to 
a URL encoded comma-separated string,
e.g. USD_JPY%2CEUR_USD
"""
def instruments_to_url(
    instruments
):
    if len(instruments) == 0:
        raise Exception
    url = ""
    for index, instrument in enumerate(instruments):
        if index < len(instruments) - 1:
            url += (instrument.get_name() + '%2C')
        else:
            url += instrument.get_name()
    return url

    
"""
Return type: string
Simply encodes a string for a url, inserting %xx as needed.
"""        
def url_encode(url):
    return urllib.parse.quote(url)
    

"""
Return type: string
Decode bytes to string using UTF8.
Parameter `b' is assumed to have type of `bytes'.
"""
def btos(b):
    if b == None:
        return None
    else:
        return b.decode('utf_8')


"""
Return type: bytes
"""
def stob(s):
    if s == None:
        return None
    else:
        return s.encode('utf_8')



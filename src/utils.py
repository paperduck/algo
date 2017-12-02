""" 
Utilities
"""


"""
Return type: string
Converts a list of <Instrument> instances to 
a URL encoded comma-separated string,
e.g. USD_JPY%2CEUR_USD
"""
def instruments_to_url(instruments):
    if len(instruments) == 0:
        raise Exception
    url = ""
    for index, instrument in enumerate(instruments):
        if index < len(instruments) - 1:
            url += (instrument.get_name() + '%2C')
        else:
            url += instrument.get_name()
    return url

            

    




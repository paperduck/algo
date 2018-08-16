"""
Take a CSV with candlestick data and convert it to a standard format for the
backtester. Standard format of columns:
    t       Microseconds since epoch
    ob      Open Bid
    oa      Open Ask
    hb      High Bid
    ha      High Ask
    lb      Low Bid
    la      Low Ask
    cb      Close Bid
    ca      Close Ask
    v       Volume
"""

from datetime import datetime as dt
import pandas as pd

def pi(path, start, end):
    """
    Only one OHLC, so duplicate prices. Spread will always be 0.
    Input:
        path:       string
        start, end: datetime
    """
    cols = ["Date","Time","Open","High","Low","Close","Volume"]
    print('Reading in CSV ({})...'.format(path))
    ret = pd.read_csv(path, dtype='str', nrows=500000)
    print('Finished reading in CSV.')
    print('Parsing date & time...')
    """ret['t'] = ret.apply(
        lambda row:
            pd.Timestamp.strptime(row['Date'] + row['Time'], '%m/%d/%Y%H%M'),
            axis=1
    )"""
    ret['t'] = pd.to_datetime(ret.Date.str.cat(ret.Time), format='%m/%d/%Y%H%M')
    print('Duplicating rest of columns...')
    ret['ob']   = ret.Open.astype('float')
    ret['oa']   = ret.Open.astype('float')
    ret['hb']   = ret.High.astype('float')
    ret['ha']   = ret.High.astype('float')
    ret['lb']   = ret.Low.astype('float')
    ret['la']   = ret.Low.astype('float')
    ret['cb']   = ret.Close.astype('float')
    ret['ca']   = ret.Close.astype('float')
    ret['v']    = ret.Volume.astype('int')
    print('dropping columns...')
    ret = ret.drop(cols, axis=1)
    print('cols dropped.')

    # trim start & end dates - TODO trim during inital load
    print('trimming off pre-start...')
    ret = ret.loc[ret['t'] > start]
    print('trimming post-end...')
    ret = ret.loc[ret['t'] < end]
    print('finished trimming.')
    return ret


"""
Take a CSV with candlestick data and convert it to a standard format.
Standard format of columns:
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

from datetime import datetime
import pandas as pd
import os

def pi(path, start, end):
    """ For CSV files from Pi Trading.

    Only one OHLC, so duplicate prices to get bid/ask.
    Spread will always be 0.
    Input:
        path:       string
        start, end: datetime
    Returns: DF with standard columns (see above)
    """
    cols = ["Date","Time","Open","High","Low","Close","Volume"]
    print('Reading in CSV ({})...'.format(path))
    
    """
    Pull one row every x rows and see if it's after start.
    If so, use i-1 as start. If not found, use i as start.
    Keep going from there to find end as well.
    """
    chunk_factor = 500
    chunk_size  = int(os.path.getsize(path) / 500)
    i           = 0
    start_i     = None # how many chunks to skip
    end_i       = None # 
    df_test     = pd.read_csv(path, header=0, dtype='str', skiprows=(chunk_size * i), nrows=1)
    print('    Seeking start ({}) and end ({})'.format(start, end), end='')
    progress = 0
    while len(df_test) > 0: # until end reached
        #print(progress); progress += 1
        dt = datetime.strptime(df_test.at[0, 'Date'] + df_test.at[0, 'Time'], '%m/%d/%Y%H%M')
        if start_i == None and dt > start: # passed start, so use i-1
            start_i = i - 1
        if dt > end: # passed end, so use i-1
            end_i = i - 1
            break            
        i += 1
        df_test = pd.read_csv(path, header=None, names=cols, dtype='str', skiprows=(chunk_size * i), nrows=1)
    print()
    # Check if CSV ended before end. Likely due to too large chunk size.
    if end_i == None:
        print('\n    csv_parse pi: End of CSV reached before finding end ({}). Path:\n{}\n'.format(end, path))
        start_i = 0
        end_i = chunk_factor + 1
    # Check if CSV starts after start
    if start_i and start_i < 0:
        print('\n    csv_parse pi: Start index is negative for start({}). Path:\n{}\n'.format(start, path))
        print('    dt = '.format(dt))
        raise Exception
    # Sanity check: If end was found, start should have been found too.
    if start_i == None and end_i:
        print('\n    csv_parse pi: Found end ({}) but not start ({}). Path:\n{}\n'.format(end, start, path))
        raise Exception
    print('    Located start and end rows. Reading into memory...')
    ret = pd.read_csv(
        path,
        header=None,
        names=cols,
        dtype='str',
        skiprows=(start_i * chunk_size),
        nrows=(((end_i - start_i) + 1) * chunk_size)
    )
    # If the headers were read in, drop that row.
    if ret.iat[0, 0] == 'Date':
        ret.drop(0, inplace=True)
    print('Parsing date & time...')
    try:
        ret['t'] = pd.to_datetime(ret.Date.str.cat(ret.Time), format='%m/%d/%Y%H%M')
    except Exception:
        import pdb; pdb.set_trace() 
    #ret.set_index(keys='t', drop=False, inplace=True) # use time as index
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
    print('Finished parsing CSV.')
    return ret


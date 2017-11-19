
"""
Module Description:    One-stop shop for configuration settings.
"""

####################
import configparser
####################
####################

class Config():
    """
    Read the config file(s) and expose the key-values pairs.
    There are two config files, a "public" one and a "private" one.
    The reason is mainly so that one can be public on GitHub. 
    If you want you can combine them into one file.
    """
    cfg = configparser.ConfigParser()

    # read the public config file
    with open('config_nonsecure.cfg', 'r') as f:
        cfg.read_file(f)
        f.close()
    _private_config_path = cfg['config_secure']['path']
    broker_name = cfg['trading']['broker']
    live_trading = False
    if cfg['trading']['live_trading'] == 'True':
        live_trading = True

    # read the private config file
    cfg.read(_private_config_path)
    oanda_url = None
    oanda_token = None
    if live_trading:
        # TODO: put the URLs in the config file
        oanda_url = 'https://api-fxtrade.oanda.com'
        oanda_token = cfg['oanda']['token']
    else:
        oanda_url =  'https://api-fxpractice.oanda.com'
        oanda_token = cfg['oanda']['token_practice']
    log_path = cfg['log']['path']
    log_file = cfg['log']['file']
    log_path = log_path + log_file
    db_user = cfg['mysql']['username']
    db_pw = cfg['mysql']['password']
    db_host = cfg['mysql']['host']
    db_name = cfg['mysql']['database']


    @classmethod
    def __str__():
        return 'Config'

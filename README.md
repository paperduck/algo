日本語下記

#Algorithmic Trading Daemon ("algo")

There are three pieces to this project, as with any algorithmic trading: backtesting, forward testing, and live trading.

## Backtesting
- Backtesting will consist of a MySQL database with historical data. The daemon iterates through the historical data to simulate live trading.
- The backtesting modules will use a strategy module as it is, so that strategy modules are blind to whether they are being used for backtesting or live trading. This eliminates the need to re-write strategy code for backtesting versus live trading.

## Forward Testing
- Same as live trading, except fake money is used.
- The "practice" variable in the config file is toggled to `True`.

## Live Trading
- The main program is referred to as a "daemon", and exists in `daemon.py`.
- Run it like this: `# python3 daemon.py`.
- Each strategy gets its own module, for example the `fifty.py` strategy module encapsulates one simple strategy.

## Platform Design
- Everything is designed with scalability and modularity in mind.
- Strategy modules can be used or not used arbitrarily, with only trivial changes to the code.
- Strategy modules can be used for backtesting, forward testing, and live trading with only trivial changes to the code.
- `daemon.py` and the strategy modules make calls to `broker.py` which makes calls to a broker-specific module specified in the config file. Having the generic `broker.py` layer allows the broker/dealer to be changed arbitrarily by only changing one line in the config file. 
- The daemon is intended to handle any number of strategies at any given time. Thus the daemon must manage margin, account balance, diversification, and other considerations when placing orders.
- This is not intended to be used for high-frequency trading.



#アルゴリズミックトレーディングボット「アルゴ」
仕掛品。    

三つ部分：（１）バックテスティング（２）フォーワードテスティング（３）③　ライブトレーディング

##　バックテスティング
MySQLでの過去の価格のデーターでシミュレーションを行うつもりです。

## フォーワードテスティング
作り物のお金の以外、ライブトレーディングと同じです。

## ライブトレーディング
自動買うのと売るの。実行し方法： `$ python3 daemon.py`

## デザイン
フレックス


![diagram](media/platform_diagram.png)





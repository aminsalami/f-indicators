import logging
import pandas as pd
import numpy as np
from backtesting import Strategy, Backtest
from talib import RSI
from backtesting.lib import crossover
from pathlib import Path, PurePosixPath

from utils import TFConvertor

log = logging.getLogger("GA")
log.setLevel(logging.DEBUG)
path = Path(__file__).parent.resolve().parent
path = path.joinpath("logs/ga.log")
log.addHandler(logging.FileHandler(path.resolve()))


data = pd.read_csv("data_large/EURUSD_Candlestick_1_M_BID_09.05.2018-30.03.2020.csv")
data['Datetime'] = pd.to_datetime(data['Datetime'], format="%d.%m.%Y %H:%M:%S")
# set datetime as index
data = data.set_index('Datetime')

data_loc = data.loc["2017":"2020"]
datatmp = TFConvertor(data_loc, '1H')   # It is different for every new individual

buy_, sell_ = 0, 0

class RSIIndicator(Strategy):
    bottom = 30
    top = 55
    price = 'Close'

    def init(self, *args, **kwargs):
        self.rsi1 = self.I(RSI, datatmp["Close"], 14)
        self.rsi2 = self.I(RSI, datatmp["Close"], 24)
        print(self.rsi1[:30])
        print(self.rsi1[len(self.rsi1)-10:])

    def next(self):
        # If signal is greater than 70, sell
        # If signal is lower than 30, buy
        if self.rsi1[-1] < self.bottom:
            global buy_
            buy_ += 1
            self.buy()
        elif self.rsi1[-1] > self.top:
            global sell_
            sell_ += 1
            self.sell()


print("Started...")
bt = Backtest(datatmp, RSIIndicator, cash=10000, commission=.02)
result = bt.run()

print(result)
print("--->", buy_, sell_)

print(np.isnan(result.SQN))
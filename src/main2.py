# Import indicators
# Attach them to strategy obj
# Start GA with strategy obj

import logging
import pandas as pd
import numpy as np
from backtesting import Strategy, Backtest
from talib import SMA
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
datatmp = TFConvertor(data_loc, '4H')   # It is different for every new individual


class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # genome:
    n1 = 2
    n2 = 6
    n3 = 10
    n4 = 20
    price = 'Close'

    def init(self, *args, **kwargs):
        # Precompute two moving averages
        self.sma1 = self.I(SMA, datatmp["Close"], self.n1)
        self.sma2 = self.I(SMA, datatmp["Close"], self.n2)
        self.sma3 = self.I(SMA, datatmp["Close"], self.n3)
        self.sma4 = self.I(SMA, datatmp["Close"], self.n4)
        # self.sma1 = SMA(datatmp["Close"], self.n1)
        # self.sma2 = SMA(datatmp["Close"], self.n2)
        # self.sma3 = SMA(datatmp["Close"], self.n3)
        # self.sma4 = SMA(datatmp["Close"], self.n4)
        # Precompute support and resistance using specified function as first input of self.I()
        # self.support_resistance = self.I(Pivot5points, self.data, self.sup_res_candles)

    def next(self):
        # If sma1 crosses above sma2, buy the asset
        if crossover(self.sma1, self.sma2) and crossover(self.sma3, self.sma4):
            try:
                print("Is buying...")
                self.buy()
            except:
                log.error("Something went wrong in buy() function!")

        # Else, if sma1 crosses below sma2, sell it
        elif crossover(self.sma2, self.sma1) and crossover(self.sma4, self.sma3):
            try:
                self.sell()
            except:
                log.error("Something went wrong in sell() function!")



bt = Backtest(datatmp, SmaCross, cash=10000, commission=.02)
result = bt.run()

print(result)

print(np.isnan(result.SQN))
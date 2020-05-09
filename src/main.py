import logging
import pandas as pd
from pathlib import Path, PurePosixPath
from genetic import BacktestingGeneticAlgorithm
from indicators.sma import SMAIndicator
from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator
from indicators.adx import ADXIndicator
from utils import CreateTimeFrames

log = logging.getLogger("GA")
log.setLevel(logging.DEBUG)
path = Path(__file__).parent.resolve().parent
path = path.joinpath("logs/ga.log")
log.addHandler(logging.FileHandler(path.resolve()))

if __name__ == "__main__":
    # log.info("Starting")
    data = pd.read_csv("data_large/EURUSD_Candlestick_1_M_BID_09.05.2018-30.03.2020.csv")
    data['Datetime'] = pd.to_datetime(data['Datetime'], format="%d.%m.%Y %H:%M:%S")
    # set datetime as index
    data = data.set_index('Datetime')

    data_slice = data.loc["2013":"2020"]

    timeframes = ['5T', '10T', '20T', '30T', '1H', '2H', '3H', '4H']
    print("[+] Prepairing time frames...")
    timeframed_data = CreateTimeFrames(data_slice, timeframes)

    # b = BacktestingGeneticAlgorithm(timeframed_data, 120, 100, 50, 20)
    b = BacktestingGeneticAlgorithm(timeframed_data, 30, 10, 5, 1, thread_size=2)

    # b.register(RSIIndicator)
    # b.register(SMAIndicator)
    b.register(MACDIndicator)
    b.register(ADXIndicator)

    b.run()

import pandas as pd
from genetic import BacktestingGeneticAlgorithm
from indicators.sma import SMAIndicator
from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator
from indicators.adx import ADXIndicator
from utils import CreateTimeFrames


if __name__ == "__main__":
    # log.info("Starting")
    data = pd.read_csv("data_large/EURUSD_Candlestick_1_M_BID_09.05.2018-30.03.2020.csv")
    data['Datetime'] = pd.to_datetime(data['Datetime'], format="%d.%m.%Y %H:%M:%S")
    # set datetime as index
    data = data.set_index('Datetime')

    data_slice = data.loc["2019":"2020"]

    # timeframes = ['5T', '10T', '20T', '30T', '1H', '2H', '3H', '4H']
    timeframes = ['1T', '3T', '5T', '30T']
    print("[+] Prepairing time frames...")
    timeframed_data = CreateTimeFrames(data_slice, timeframes)

    # b = BacktestingGeneticAlgorithm(timeframed_data, 120, 100, 50, 20)
    b = BacktestingGeneticAlgorithm(
        timeframed_data,
        population_size=65,
        generations=20,
        number_of_xover=30,
        number_of_jesus=20,
        thread_size=8
    )

    b.register(RSIIndicator)
    # b.register(SMAIndicator)
    b.register(MACDIndicator)
    b.register(ADXIndicator)

    b.run()

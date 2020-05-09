import random
from talib import MACD
from base import BaseStrategy


class MACDParameter(object):
    """
    MACD Line: The MACD line is the heart of the indicator and by default it’s the
    difference between the 12-period EMA and the 26-period EMA. This means that
    the MACD line is basically a complete moving average crossover system by itself.

    Signal Line: The Signal line is the 9-period EMA of MACD Line

    MACD Histogram: MACD Line – Signal Line
    """
    def __init__(self):
        self.bottom = random.randint(2, 25)             # fast_period
        self.top = random.randint(self.bottom, 50)      # slow_period
        self.period = random.randint(1, 25)             # signal_period

    def xover(self, obj):
        """
        xover this object with another `Indicator` of the same type.
        Create a new object and return it
        NOTE: The `obj` has lower fitness
        """
        p = MACDParameter()
        tmp = random.randint(1, 100)
        if tmp < 30:
            p.bottom = self.bottom
            p.top = obj.top if obj.top > self.bottom else random.randint(min(self.bottom, 25), self.top)
            p.period = self.period

        elif tmp < 60:
            p.bottom = obj.bottom
            p.top = self.top if self.top > obj.bottom else random.randint(p.bottom, 50)
            p.period = obj.period

        else:
            p.bottom = self.bottom + random.randint(-4, 4)
            if p.bottom < 2:
                p.bottom = 2
            p.top = self.top + random.randint(-4, 4)
            p.period = random.randint(min(self.period, obj.period), max(self.period, obj.period))
            if p.top <= p.bottom:
                p.top = random.randint(p.bottom, 50)

        return p

    def mutate(self):
        self.bottom = random.randint(2, 25)
        self.top = self.top + random.randint(-5, 5)
        if self.top <= self.bottom:
            self.top = random.randint(self.bottom, 50)
        self.period = random.randint(5, 30)

    def get_params(self):
        # (fast_period, slow_period, signal_period)
        return (self.bottom, self.top, self.period)


class MACDIndicator(BaseStrategy):
    """
    """
    name = "MACD"

    params = MACDParameter

    def next(self) -> int:
        if self.macd_macd[-1] > self.macd_signal[-1] and self.macd_macd[-2] > self.macd_signal[-2]:
            # Buy
            return 1
        elif self.macd_macd[-1] < self.macd_signal[-1] and self.macd_macd[-2] < self.macd_signal[-2]:
            # Sell
            return -1
        else:
            return 0

    def init(self):
        self.macd_macd, self.macd_signal, _ = self.I(MACD, self.data['Close'], self.params_MACD.bottom, self.params_MACD.top, self.params_MACD.period)

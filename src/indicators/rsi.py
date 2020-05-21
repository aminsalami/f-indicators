import random
from talib import RSI
from base import BaseStrategy


# h_rsi_candles = 3
# h_rsi_tresh = 70
# l_rsi_candles = 6
# l_rsi_tresh = 30

MIN1 = 25
MIN2 = 35
MAX1 = 65
MAX2 = 75

class RSIParameter(object):
    def __init__(self):
        self.bottom = random.randint(MIN1, MIN2)
        self.top = random.randint(MAX1, MAX2)
        self.period_A = 14

    def xover(self, obj):
        """
        xover this object with another `Indicator` of the same type.
        Create a new object and return it
        NOTE: The `obj` has lower fitness
        """
        tmp = random.randint(1, 100)
        p = RSIParameter()
        if tmp < 30:
            p.bottom = self.bottom
            p.top = obj.top
        elif tmp < 60:
            p.bottom = obj.bottom
            p.top = self.top
        else:
            p.bottom = self.bottom + random.randint(-2, +2)
            p.top = self.top + random.randint(-2, +2)

        return p

    def mutate(self):
        self.bottom = random.randint(MIN1, MIN2)
        self.top = random.randint(MAX1, MAX2)

    def get_params(self):
        return ("RSI", self.bottom, self.top, self.period_A)

    def check_distance(self, bottom, top, min_distance=10):
        while top - bottom < min_distance:
            top += 1
            bottom -= 1
        if bottom <= 0:
            return 0, min_distance
        return bottom, top


class RSIIndicator(BaseStrategy):
    """
    """
    name = "RSI"

    params = RSIParameter

    def next(self) -> int:
        if self.lrsi[-1] < self.params_RSI.bottom:
            # buy
            return 1
        elif self.hrsi[-1] > self.params_RSI.top:
            # sell
            return -1
        else:
            return 0

    def init(self):
        self.lrsi = self.I(RSI, self.data["Low"], 6)
        self.hrsi = self.I(RSI, self.data["High"], 3)

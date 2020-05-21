import random
from talib import RSI
from base import BaseStrategy


class RSIParameter(object):
    def __init__(self):
        self.bottom = 40
        self.top = 50
        self.period_A = 14
        self.price = random.choice(["Open", "Close", "Low", "High"])

    def xover(self, obj):
        """
        xover this object with another `Indicator` of the same type.
        Create a new object and return it
        NOTE: The `obj` has lower fitness
        """
        tmp = random.randint(1, 100)
        if tmp > 60:
            return obj
        return self

    def mutate(self):
        self.price = random.choice(["Open", "Close", "Low", "High"])

    def get_params(self):
        return ("RSI", self.bottom, self.top, self.period_A, self.price)

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
        if self.rsi_A[-1] < self.params_RSI.bottom:
            # buy
            return 1
        elif self.rsi_A[-1] > self.params_RSI.top:
            # sell
            return -1
        else:
            return 0

    def init(self):
        price = self.params_RSI.price
        self.rsi_A = self.I(RSI, self.data[price], self.params_RSI.period_A)

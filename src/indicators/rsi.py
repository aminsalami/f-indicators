import random
from talib import RSI
from base import BaseStrategy


class RSIParameter(object):
    def __init__(self):
        self.bottom = random.randint(1, 50)
        self.top = random.randint(50, 100)
        self.period_A = random.randint(2, 30)
        self.price = random.choice(["Open", "Close", "Low", "High"])

    def xover(self, obj):
        """
        xover this object with another `Indicator` of the same type.
        Create a new object and return it
        NOTE: The `obj` has lower fitness
        """
        p = RSIParameter()
        tmp = random.randint(1, 100)
        if tmp < 30:
            p.bottom = self.bottom
            p.top = obj.top if obj.top > self.bottom else random.randint(min(self.bottom, 50), self.top)
            p.period_A = self.period_A
            p.price = obj.price

        elif tmp < 60:
            p.bottom = obj.bottom
            p.top = self.top if self.top > obj.bottom else random.randint(max(self.top, 50), 100)
            p.period_A = obj.period_A
            p.price = self.price

        else:
            p.bottom = self.bottom + random.indint(-4, 4)
            p.top = self.top + random.randint(-4, 4)
            p.period_A = random.randint(min(self.period_A, obj.period_A), max(self.period_A, obj.period_A))
            p.price = random.choice(["Open", "Close", "Low", "High"])

            if p.top <= p.bottom:
                p.top = random.randint(p.bottom, 100)

        return p

    def mutate(self):
        self.bottom = self.bottom + random.choice([8, -8])
        self.top = self.top + random.choice([8, -8])
        if self.top <= self.bottom:
            self.top = random.randint(self.bottom, 100)
        self.period_A = random.randint(10, 20)

    def get_params(self):
        return (self.bottom, self.top, self.period_A)


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

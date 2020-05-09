import random
from talib import ADX
from base import BaseStrategy


class ADXParameter(object):
    def __init__(self):
        self.period = random.randint(2, 30)
        self.bottom = random.randint(10, 30)
        self.top = random.randint(self.bottom, 40)

    def xover(self, obj):
        """
        xover this object with another `Indicator` of the same type.
        Create a new object and return it
        NOTE: The `obj` has lower fitness
        """
        p = ADXParameter()
        tmp = random.randint(1, 100)
        if tmp < 30:
            p.period = self.period
            p.bottom = obj.bottom
            p.top = self.top if self.top > p.bottom else random.randint(p.bottom, 40)

        elif tmp < 60:
            p.period = obj.period
            p.bottom = self.bottom
            p.top = obj.top if obj.top > p.bottom else random.randint(p.bottom, 40)

        else:
            p.period = random.randint(6, 30)
            p.bottom = self.bottom
            p.top = random.randint(min(self.top, obj.top), max(self.top, obj.top))
            if p.top <= p.bottom:
                p.top = random.randint(p.bottom+1, 40)

        return p

    def mutate(self):
        self.period = self.period + random.randint(-2, 2)
        if self.period < 2:
            self.period = 3     # pffff
        self.bottom = self.bottom + random.randint(-2, 2)
        self.top = self.top + random.randint(-2, 2)
        if self.top <= self.bottom:
            self.top = random.randint(self.bottom+1, 40)

    def get_params(self):
        return (self.period)


class ADXIndicator(BaseStrategy):
    """
    """
    name = "ADX"

    params = ADXParameter

    def next(self) -> int:
        if self.adx_signal[-1] > self.params_ADX.top and self.adx_signal[-2] > self.params_ADX.top:
            # Buy
            return +1
        elif self.adx_signal[-1] < self.params_ADX.bottom and self.adx_signal[-2] < self.params_ADX.bottom:
            # Sell
            return -1
        else:
            # Do nothing
            return 0

    def init(self):
        self.adx_signal = self.I(ADX, self.data['High'], self.data['Low'], self.data['Close'], self.params_ADX.period)

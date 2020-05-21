import random
from talib import MACD
from base import BaseStrategy



# h_macd_slow_period = 15
# h_macd_fast_period = 6
# h_macd_tresh = 0.0001

# l_macd_slow_period = 19
# l_macd_fast_period = 5
# l_macd_tresh = -0.00013

class MACDParameter(object):
    """
    MACD Line: The MACD line is the heart of the indicator and by default it’s the
    difference between the 12-period EMA and the 26-period EMA. This means that
    the MACD line is basically a complete moving average crossover system by itself.

    Signal Line: The Signal line is the 9-period EMA of MACD Line

    MACD Histogram: MACD Line – Signal Line
    """
    def __init__(self):
        self.period = 9
        # Low
        self.lbottom = random.randint(2, 8)     # fast_period
        self.ltop = random.randint(16, 22)      # slow_period
        self.ltresh = -0.00013 + random.randint(-6, +6)/200000

        # High
        self.hbottom = random.randint(3, 9)     # fast_period
        self.htop = random.randint(12, 18)      # slow_period
        self.htresh = 0.0001 + random.randint(-6, +6)/200000

    def xover(self, obj):
        """
        xover this object with another `Indicator` of the same type.
        Create a new object and return it
        NOTE: The `obj` has lower fitness
        """
        p = MACDParameter()
        tmp = random.randint(1, 100)
        if tmp < 30:
            p.ltresh = self.ltresh
            p.htresh = self.htresh
            p.lbottom = self.lbottom
            p.hbottom = self.hbottom

            p.ltop = obj.ltop if obj.ltop > self.lbottom else random.randint(min(self.lbottom, 8), self.ltop)
            p.htop = obj.htop if obj.htop > self.hbottom else random.randint(min(self.hbottom, 9), self.htop)
            p.period = self.period

        elif tmp < 60:
            p.ltresh = obj.ltresh
            p.htresh = obj.htresh
            p.lbottom = obj.lbottom
            p.hbottom = obj.hbottom

            p.ltop = self.ltop if self.ltop > obj.lbottom else random.randint(p.lbottom, 8)
            p.htop = self.htop if self.htop > obj.hbottom else random.randint(p.hbottom, 9)
            p.period = obj.period

        else:
            p.htresh =  self.htresh + random.randint(-3, +3)/100000
            p.ltresh =  self.ltresh + random.randint(-3, +3)/100000
            p.lbottom = self.lbottom + random.randint(-1, 1)
            p.hbottom = self.hbottom + random.randint(-1, 1)
            if p.lbottom < 2:
                p.lbottom = 2
            if p.hbottom < 2:
                p.hbottom = 2
            p.ltop = self.ltop + random.randint(-1, 1)
            p.period = random.randint(min(self.period, obj.period), max(self.period, obj.period))
            if p.ltop <= p.lbottom:
                p.ltop = random.randint(p.lbottom, 22)
            if p.htop <= p.hbottom:
                p.htop = random.randint(p.hbottom, 18)

        return p

    def mutate(self):
        self.ltresh = -0.00013 + random.randint(-6, +6)/200000
        self.htresh = 0.0001 + random.randint(-6, +6)/200000
        self.lbottom = random.randint(2, 8)
        self.hbottom = random.randint(3, 9)
        self.ltop = self.ltop + random.randint(-1, 1)
        self.htop = self.htop + random.randint(-1, 1)
        if self.ltop <= self.lbottom:
            self.ltop = random.randint(self.lbottom, 22)
        if self.htop <= self.hbottom:
            self.htop = random.randint(self.hbottom, 18)

    def get_params(self):
        # (fast_period, slow_period, signal_period)
        return ("MACD", self.lbottom, self.ltop, self.hbottom, self.htop, self.ltresh, self.htresh)


class MACDIndicator(BaseStrategy):
    """
    """
    name = "MACD"

    params = MACDParameter

    def next(self) -> int:
        if not self.bought and self.lmacd[-1] < self.params_MACD.ltresh:
            # Buy
            self.bought = not self.bought
            return 1
        elif self.bought and self.hmacd[-1] < self.params_MACD.htresh and self.hmacd[-2] > self.params_MACD.htresh:
            # Sell
            self.bought = not self.bought
            return -1
        else:
            return 0

    def init(self):
        self.bought = False
        self.lmacd, _, _ = self.I(MACD, self.data['Low'], self.params_MACD.lbottom, self.params_MACD.ltop, self.params_MACD.period)
        self.hmacd, _, _ = self.I(MACD, self.data['High'], self.params_MACD.hbottom, self.params_MACD.htop, self.params_MACD.period)

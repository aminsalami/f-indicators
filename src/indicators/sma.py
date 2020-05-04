import random
from talib import SMA
from base import BaseStrategy
from backtesting.lib import crossover


class SMAParameter(object):
    OPEN = "Open"
    CLOSE = "Close"
    LOW = "Low"
    HIGH = "High"

    statuses = [OPEN, CLOSE, LOW, HIGH]

    def __init__(self):
        my_ass = random.sample(range(2, 200), 2)
        my_ass2 = random.sample(range(2, 200), 2)
        self.A = min(my_ass)
        self.B = max(my_ass)
        self.C = min(my_ass2)
        self.D = max(my_ass2)
        self.price = random.choice(self.statuses)
        # print("NEW SMA PARAMETER:", self.A, self.B, self.C, self.D)

    def mutate(self):
        tmp = random.randint(0, 100)

        if(tmp < 22.5):
            self.A = random.randint(1, self.B)
        elif(tmp < 45):
            self.B = random.randint(self.A, 200)
        elif(tmp < 68):
            self.C = random.randint(1, self.D)
        elif(tmp < 90):
            self.D = random.randint(self.C, 200)
        elif(tmp < 100):
            self.price = random.choice(self.statuses)

    def xover(self, obj):
        """
        xover this object with another `Indicator` of the same type.
        Create a new object and return it

        NOTE: The `obj` has lower fitness
        """
        if not isinstance(obj, SMAParameter):
            raise TypeError
        p = SMAParameter()
        tmp = random.randint(1, 100)

        if tmp < 20:
            p.A = self.A
            p.B = self.B
            p.C = obj.C
            p.D = obj.D
            p.price = self.price

        elif tmp < 40:
            p.A = obj.A
            p.B = obj.B
            p.C = self.C
            p.D = self.D
            p.price = obj.price

        elif tmp < 100:
            if self.A <= obj.A:
                p.A = random.randint(self.A, int((self.A + obj.A) / 2))
            else:
                p.A = random.randint(int((self.A+obj.A)/2), self.A)

            if self.B <= obj.B:
                p.B = random.randint(self.B, int((self.B+obj.B)/2))
            else:
                p.B = random.randint(int((self.B+obj.B)/2), self.B)

            if self.C <= obj.C:
                p.C = random.randint(self.C, int((self.C+obj.C)/2))
            else:
                p.C = random.randint(int((self.C+obj.C)/2), self.C)

            if self.D <= obj.D:
                p.D = random.randint(self.D, int((self.D+obj.D)/2))
            else:
                p.D = random.randint(int((self.D+obj.D)/2), self.D)

            p.price = self.price

        return p

    def get_params(self):
        return (self.A, self.B, self.C, self.D, self.price)
# ----------------------------------------------------------------------------

class SMAIndicator(object):
    """
    """
    # Every class MUST provide a unique name to be recognized by
    # the individual
    name = "SMA"

    params = SMAParameter

    def next(self) -> int:
        if crossover(self.sma_A, self.sma_B) and crossover(self.sma_C, self.sma_D):
            return 1
        elif crossover(self.sma_B, self.sma_A) and crossover(self.sma_D, self.sma_C):
            return -1
        # Default value for transaction!
        return 0

    def init(self):
        """
        Initialize data
        NOTE: This method is called after backtest.run()
        """
        price = self.params_SMA.price
        self.sma_A = self.I(SMA, self.data[price], self.params_SMA.A)
        self.sma_B = self.I(SMA, self.data[price], self.params_SMA.B)
        self.sma_C = self.I(SMA, self.data[price], self.params_SMA.C)
        self.sma_D = self.I(SMA, self.data[price], self.params_SMA.D)
        # print("PARAMETERS:\n", period_A, period_B, period_C, period_D)

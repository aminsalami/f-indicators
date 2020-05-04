from abc import ABCMeta, abstractmethod
import numpy as np
from backtesting import Strategy

class BaseGaIndividualInterface(metaclass=ABCMeta):
    """
    Base Genetic Algorithm Individual
    All individuals SHOULD inherit from this class and implement its methods.
    """
    @abstractmethod
    def xover(self):
        raise NotImplementedError

    @abstractmethod
    def mutate(self):
        raise NotImplementedError
# ----------------------------------------------------------------------------


class BaseStrategy(Strategy):
    """
    """
    def init(self):
        """
        Initialize the strategy.
        Declare indicators (with `backtesting.backtesting.Strategy.I`).
        Precompute what needs to be precomputed or can be precomputed
        in a vectorized fashion before the strategy starts.
        """
        for method in dir(self):
            if method.startswith("init__"):
                init = getattr(self, method)
                init()

    def next(self):
        """
        Buy if sum of transactions is greater than zero.
        """
        buy_or_not = 0

        for method in dir(self):
            if method.startswith("next__"):
                next_ = getattr(self, method)
                buy_or_not += next_()

        if buy_or_not > 0:
            self.buy()
        elif buy_or_not < 0:
            self.sell()
# ----------------------------------------------------------------------------

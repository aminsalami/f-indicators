# Implements 'Individual GA' class
import logging
from datetime import datetime
import random
import numpy as np
from pathlib import Path
from backtesting import Strategy, Backtest
from base import BaseGaIndividualInterface, BaseStrategy
from indicators.sma import SMAIndicator
from utils import TFConvertor
# ----------------------------------------------------------------------------
log = logging.getLogger("Individual")
log.setLevel(logging.DEBUG)
path = Path(__file__).parent.resolve().parent
path = path.joinpath("logs/ga__%s.log" % datetime.now().strftime('%Y-%m-%d--%H:%M:%S'))
log.addHandler(logging.FileHandler(path.resolve()))


class BaseIndividual(BaseGaIndividualInterface):
    """
    """
    def __init__(self, data, cash=10000, commission=0.0002, *args, **kwargs):
        self.original_data = data
        self.timeframe = random.choice(list(data.keys()))
        self.sample_data = data[self.timeframe]
        self.commission = commission
        self.cash = cash

        self._indicators_class = []
        self.strategy_cls = None

        self.result = None
        self._fitness = None
        self.duplicate_number = 1
        self.delete_probability = None

    def xover(self):
        """Use + operator to xover two individuals"""
        pass

    def __add__(self, obj):
        """xover two individuals"""
        if not isinstance(obj, BaseIndividual):
            raise TypeError

        ind1_params = []
        ind2_params = []
        for p in dir(self.strategy_cls):
            if p.startswith('params_'):
                ind1_params.append(getattr(self.strategy_cls, p))

        for p in dir(obj.strategy_cls):
            if p.startswith('params_'):
                ind2_params.append(getattr(obj.strategy_cls, p))

        # Create a new child and populate its value
        ind = BaseIndividual(self.original_data, self.cash, self.commission)
        for k in self._indicators_class:
            ind.register(k)

        new_params = []
        for p1, p2 in zip(ind1_params, ind2_params):
            # XOver parameter1 and parameter2
            # TODO check if xover() returns a valid parameter object
            if self.fitness > obj.fitness:
                new_params.append(p1.xover(p2))
            else:
                new_params.append(p2.xover(p1))

        ind.strategy_cls = ind._build_strategy(new_params.reverse())
        ind.sample_data = random.choice([obj.sample_data, self.sample_data])
        # Recalculate the fitness
        ind.fitness
        log.debug("XOver (%s, %s) --> %s" % (self.fitness, obj.fitness, ind.fitness))
        return ind

    def mutate(self):
        for p in dir(self.strategy_cls):
            if p.startswith('params_'):
                p = getattr(self.strategy_cls, p)
                p.mutate()
        # Recalculate the fitness
        self._calculate_fitness()

    def get_params(self):
        params = []
        for p in dir(self.strategy_cls):
            if p.startswith('params_'):
                params.append(getattr(self.strategy_cls, p))
        return [p.get_params() for p in params]

    @property
    def fitness(self) -> float:
        if not self._fitness:
            self._fitness = self._calculate_fitness()
        return self._fitness

    def _calculate_fitness(self) -> float:
        """
        Calculate fitness for each one of the strategies and return the result.
        """
        bt = Backtest(self.sample_data, self.strategy_cls, cash=self.cash, commission=self.commission)
        result = bt.run()
        self.result = result
        if np.isnan(result.SQN):
            sqn = -70.0
        else:
            sqn = result.SQN
        self._fitness = sqn
        return sqn

    def register(self, klass):
        """
        """
        # klass is of type BaseIndicator
        self._indicators_class.append(klass)

    def _build_strategy(self, parameters):
        methods = {}
        for i, klass in enumerate(self._indicators_class):
            name = klass.__dict__.get('name')
            methods['init__' + str(i) + name] = klass.__dict__.get('init')
            methods['next__' + str(i) + name] = klass.__dict__.get('next')
            if parameters:
                methods['params_' + name] = parameters.pop(0)
            else:
                p = klass.__dict__.get('params')
                methods['params_' + name] = p()

        return type("DynStrategy", (BaseStrategy, ), methods)

    def build_strategy(self):
        """
        TODO Check for errors!
        NOTE I can initialize the class parameters here. Or I can just let the
            backtesting.run() do it for me by calling the reset() method.
        TODO This is just a HOTFIX
        TODO Maybe its a good solution to bound single functions to strategy_cls
        """
        self.strategy_cls = self._build_strategy(parameters=None)

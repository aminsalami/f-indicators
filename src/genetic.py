# Genetic Algorithm implementation for backtesting lib

import random
import time
import threading
from collections import Counter
from individual import BaseIndividual
from utils import DuplicateCounter

class BacktestingGeneticAlgorithm(object):
    """
    TODO Load GA parameters from a config file
    TODO Pass individual parameters as a TradeConfigObject
    """

    def __init__(self, data, population_size=100, generations=100, number_of_xover=50,
        number_of_jesus=30, mutation_probability=0.1, thread_size=4):
        self._thread_size = thread_size
        self._data = data
        self._population_size = population_size
        self._generations = generations
        self._number_of_xover = number_of_xover
        self._number_of_jesus = number_of_jesus
        self._mutation_probability = mutation_probability

        self._indicator_classes = []
        self._population = []

    def _new_population(self, size=None) -> list:
        if not size:
            size = self._population_size
        for _ in range(size):
            self._add_individual()

    def _add_individual(self):
        ind = BaseIndividual(self._data)
        for indicator in self._indicator_classes:
            ind.register(indicator)
        # Build strategy based on registered indicators
        ind.build_strategy()
        # print("[+] Fitness:", ind.fitness)
        ind.fitness # Force fitness to be calculated
        self._population.append(ind)

    def _add_jesus(self):
        for _ in range(self._number_of_jesus):
            self._add_individual()

    def _do_xover(self):
        # select two individual
        ind1, ind2 = random.sample(self._population, 2)
        new_ind = ind1 + ind2   # xover two individuals
        new_ind.data = self._data

        self._do_mutate(new_ind)

        self._population.append(new_ind)

    def _do_mutate(self, ind):
        if random.random() < self._mutation_probability:
            ind.mutate()

    def _do_survive(self):
        print('Number of population:', len(self._population))
        c = DuplicateCounter()
        # to_be_distinct = set()
        for ind in self._population:
            params = ind.get_params()
            c[params] = ind

        new_population = c.count()
        # print("Max fitness:", self.max_fitness)
        for ind in new_population:
            # Old delete_probability for positive max_fitness =  occurrence/population_len + 1-fitness/max(fitness)
            t = ind.result.get("Avg. Trade Duration") # Average Trade Duration
            tph = t.total_seconds() / 3600  # Average Trade Duration per Hour
            ind.delete_probability = 5*ind.duplicate_number/len(new_population) - ind.fitness/tph

        new_population = sorted(new_population, key=lambda x: x.delete_probability)
        self._population = new_population[:self._population_size]

    def register(self, obj):
        """
        Register indicators as chromosomes
        """
        self._indicator_classes.append(obj)

    def run(self):
        threads = []
        for _ in range(self._thread_size):  # TODO Make thread size dynamic
            threads.append(threading.Thread(target=self._new_population, args=(int(self._population_size/self._thread_size), )))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        print("\n==Population created successfully!==\n")

        for _ in range(self._generations):
            # Add random individual
            self._add_jesus()
            # random Xover
            for _ in range(self._number_of_xover):
                self._do_xover()

            self._do_survive()

        print('Number of population:', len(self._population))
        print("\n\n", self._population[0].result)
        print("\n\n", self._population[0].get_params())
        print("\nDone GA :)\n")

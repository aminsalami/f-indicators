# Genetic Algorithm implementation for backtesting lib

import random
import time
from collections import Counter
from individual import BaseIndividual
from utils import DuplicateCounter

class BacktestingGeneticAlgorithm(object):
    """
    TODO Load GA parameters from a config file
    TODO Pass individual parameters as a TradeConfigObject
    """

    def __init__(self, data, population_size=100, generations=100, number_of_xover=50, number_of_jesus=30, mutation_probability=0.1):
        self._data = data
        self._population_size = population_size
        self._generations = generations
        self._number_of_xover = number_of_xover
        self._number_of_jesus = number_of_jesus
        self._mutation_probability = mutation_probability

        self._indicator_classes = []
        self._population = []
        self.max_fitness = -70

    def _new_population(self) -> list:
        """
        TODO
            Create populations in a concurrent way and force
            the fitness value to be calculated
        """
        for _ in range(self._population_size):
            self._add_individual()

    def _add_individual(self):
        ind = BaseIndividual(self._data)
        for indicator in self._indicator_classes:
            ind.register(indicator)
        # Build strategy based on registered indicators
        ind.build_strategy()
        # print("[+] Fitness:", ind.fitness)
        if self.max_fitness < ind.fitness:
            self.max_fitness = ind.fitness
        self._population.append(ind)

    def _add_jesus(self):
        for _ in range(self._number_of_jesus):
            self._add_individual()

    def _do_xover(self):
        # select two individual
        ind1, ind2 = random.sample(self._population, 2)
        new_ind = ind1 + ind2
        new_ind.data = self._data   # xover two individuals

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
            # delete_probability for positive max_fitness =  5*occurrence/population_len + 1-fitness/max(fitness)
            # delete_probability for negative max_fitness =  5*occurrence/population_len + 1+fitness/max(fitness)
            max_fitness = self.max_fitness * -1
            ind.survive_probability = 5*ind.duplicate_number/len(new_population) + 1 + ind.fitness/max_fitness

        new_population = sorted(new_population, key=lambda x: x.survive_probability, reverse=True)
        # for p in new_population:
            # print(p.fitness, p.duplicate_number, p.survive_probability)
        self._population = new_population[:self._population_size]

    def register(self, obj):
        """
        Register indicators as chromosomes
        """
        self._indicator_classes.append(obj)

    def run(self):
        self._new_population()
        print("\n==Population created successfully!==\n")
        for _ in range(self._generations):
            # Add random individual
            self._add_jesus()
            # random Xover
            for _ in range(self._number_of_xover):
                self._do_xover()

            self._do_survive()

        print('Number of population:', len(self._population))
        print("\nFITNESS MAX:", self.max_fitness)
        print("\n\n", self._population[0].result)
        print("\n\n", self._population[0].get_params())
        print("Done GA :)\n")

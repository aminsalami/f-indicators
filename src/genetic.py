# Genetic Algorithm implementation for backtesting lib
import logging
from datetime import datetime
import random
import time
import threading
import numpy.random as npr
from pathlib import Path
from collections import Counter
from individual import BaseIndividual
from utils import DuplicateCounter

log = logging.getLogger("GA")
log.setLevel(logging.DEBUG)
path = Path(__file__).parent.resolve().parent
path = path.joinpath("logs/ga__%s.log" % datetime.now().strftime('%Y-%m-%d--%H:%M:%S'))
log.addHandler(logging.FileHandler(path.resolve()))


class BacktestingGeneticAlgorithm(object):
    """
    TODO Load GA parameters from a config file
    TODO Pass individual parameters as a TradeConfigObject
    """

    def __init__(self, data, population_size, generations, number_of_xover,
        number_of_jesus, mutation_probability=0.1, thread_size=4):
        self._thread_size = thread_size
        self._data = data
        self._population_size = population_size
        self._generations = generations
        self._number_of_xover = number_of_xover
        self._number_of_jesus = number_of_jesus
        self._mutation_probability = mutation_probability

        self._indicator_classes = []
        self._population = []

    def _new_population(self, size=None):
        if size is None:
            size = self._population_size
        for _ in range(size):
            self._add_individual()

    def _add_individual(self):
        ind = BaseIndividual(self._data)
        for indicator in self._indicator_classes:
            ind.register(indicator)
        # Build strategy based on registered indicators
        ind.build_strategy()
        ind.fitness # Force fitness to be calculated
        self._population.append(ind)

    def _add_jesus(self):
        if self._number_of_jesus <= 0:
            return
        threads = []
        size = self._number_of_jesus//self._thread_size
        for _ in range(self._thread_size - 1):
            threads.append(threading.Thread(target=self._new_population, args=(size, )))
        threads.append(threading.Thread(target=self._new_population, args=(size + self._number_of_jesus % self._thread_size, )))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self._number_of_jesus -= 1

    def _do_xover(self):
        fitness_vector = [i.fitness for i in self._population]
        # Select two random indexes based on fitness_values
        indx1, indx2 = self.roulette_wheel(fitness_vector)
        log.debug("roulette_wheel selected: %s, %s" % (indx1, indx2))
        ind1, ind2 = self._population[indx1], self._population[indx2]
        new_ind = ind1 + ind2   # xover two individuals
        new_ind.data = self._data

        self._do_mutate(new_ind)

        self._population.append(new_ind)

    def _do_mutate(self, ind):
        if random.random() < self._mutation_probability:
            ind.mutate()

    def _do_survive(self):
        c = DuplicateCounter()
        for ind in self._population:
            params = ind.get_params()
            c[params] = ind

        new_population = c.count()
        for ind in new_population:
            # Old delete_probability for positive max_fitness =  occurrence/population_len + 1-fitness/max(fitness)
            t = ind.result.get("Avg. Trade Duration") # Average Trade Duration
            atd = t.total_seconds() / 3600  # Average Trade Duration in Hour
            ind.delete_probability = 5*ind.duplicate_number/len(new_population) - ind.fitness/atd
            # ind.delete_probability = 2*ind.duplicate_number/len(new_population) - ind.fitness

        new_population = sorted(new_population, key=lambda x: x.delete_probability)
        self._population = new_population[:self._population_size]

    def register(self, obj):
        """
        Register indicators as chromosomes
        """
        self._indicator_classes.append(obj)

    def roulette_wheel(self, vector):
        # Normalize fitness values to [0, 1]
        maxi = max(vector)
        mini = min(vector)
        normalized = [(f - mini)/(maxi-mini) for f in vector]

        # Calculate selection probability
        vector_sum = sum(normalized)
        selection_probability = [f/vector_sum for f in normalized]

        # select two individual
        select1 = npr.choice(len(vector), p=selection_probability)
        select2 = npr.choice(len(vector), p=selection_probability)
        while select1 == select2:
            # Select two different values
            select2 = npr.choice(len(vector), p=selection_probability)
        return select1, select2

    def run(self):
        threads = []
        size = self._population_size // self._thread_size
        for _ in range(self._thread_size - 1):
            threads.append(threading.Thread(target=self._new_population, args=(size, )))
        threads.append(threading.Thread(target=self._new_population, args=(size + self._population_size % self._thread_size, )))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        print("\n[+] Population created successfully.\n")

        for _ in range(self._generations):
            log.info("\n--- New Generation ---\n")
            # Add random individual
            self._add_jesus()
            # random Xover
            for _ in range(self._number_of_xover):
                self._do_xover()
            # Remove bad genomes
            self._do_survive()
            # Increase mutation probability
            self._mutation_probability += 0.35/self._generations

            p0 = self._population[0]
            print("Fitness, TimeFrame, Trades#, AvgDuration: (%s, %s, %s, %s)" % \
                (p0.fitness, p0.timeframe, p0.result.get("# Trades"), p0.result.get("Avg. Trade Duration"))
                )
            log.debug("Best individual result")
            log.debug(p0.result)

        log.info("Final mutation probability: %s" % self._mutation_probability)
        print("\n\n", self._population[0].result)
        print("\n\n", self._population[0].get_params())
        print("\nDone GA :)\n")

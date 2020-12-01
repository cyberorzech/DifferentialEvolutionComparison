from progressbar import ProgressBar
from tqdm import tqdm
import numpy as np

from src.evaluators import Evaluate


class ClassicDE:

    # Derivatives
    dimensions = 0
    normalized_population = np.empty([dimensions, population_size])
    denorm_population = np.empty([dimensions, population_size])
    values_array = np.empty([dimensions, population_size], int)

    def __init__(self, bounds, mutation, cross_probability, population, iterations, clip, cost_function):
        self.bounds = bounds
        self.mutation = mutation
        self.cross_probability = cross_probability,
        self.population = population
        self.iterations = iterations
        self.clip = clip
        self.population_size = len(population)
        self.cost_function = cost_function
        # set parameters above given from main.py
        self.dimensions = len(self.bounds)
        self.best_vector = np.empty([1])
        self.best_index = -1
        self.initialize_population()

    def de(self):
        for i in tqdm(range(self.iterations)):
            for j in range(self.population_size):
                indexes_except_best = [ind for ind in range (self.population_size) if ind != j]
                vector_a, vector_b, vector_c = self.normalized_population[np.random.choice(indexes_except_best, 3, replace=False)]

                # Clip or Draw - to implement
                mutant = np.clip(vector_a + self.mutation * (vector_b - vector_c), 0, 1)
                cross_points = np.random.rand(self.dimensions) < self.cross_probability
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, self.dimensions)] = True
                candidating_vect = np.where(cross_points, mutant, self.normalized_population[j])
                candidating_denorm = self.denorm(candidating_vect)

                # self.update(self.testing_func(candidating_denorm), candidating_denorm, candidating_vect, j)
                self.update(self.cost_function.levy(candidating_denorm), candidating_denorm, candidating_vect, j)
            yield self.best_vector, self.values_array[self.best_index]


    def initialize_population(self):
        self.normalized_population = np.random.rand(self.population_size, self.dimensions)
        self.denorm_population = self.denorm(self.normalized_population)
        self.best_vector = self.find_best_vector(self.denorm_population)

    def denorm(self, normalized_population):
        # check if bounds are given in proper order
        min_bound, max_bound = np.asarray(self.bounds).T
        bounds_difference = np.fabs(min_bound - max_bound)
        return max_bound - bounds_difference * normalized_population

    def find_best_vector(self, denorm_population):
        # self.values_array = np.asarray([self.testing_func(ind) for ind in denorm_population])
        self.values_array = np.asarray([self.cost_function.levy(ind) for ind in denorm_population])
        self.best_index = np.argmin(self.values_array)
        return denorm_population[self.best_index]

    def update(self, candidate, denorm_candidate, norm_candidate, j):
        if candidate < self.values_array[j]:
            self.values_array[j] = candidate
            self.normalized_population[j] = norm_candidate
            if candidate < self.values_array[self.best_index]:
                self.best_index = j
                self.best_vector = denorm_candidate

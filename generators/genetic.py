""" Genetic creation """
from datetime import datetime
from random import choices, randint, randrange, random, sample
from typing import List, Callable, Tuple

from .base import MusicGenerator
from structures import MusicUnit
from converters.unit import binary_to_unit

GenomeType = List[int]
PopulationType = List[GenomeType]
FitnessFunctionType = Callable[[GenomeType], int]


class GeneticGenerator(MusicGenerator):
    # Type aliases for better readability

    # Genetic evolution functions
    def __init__(self,
                fitness_func: FitnessFunctionType,
                 size: int,
                 genome_length: int,
                 fitness_limit: int,
                generation_limit: int = 100):
        super().__init__()
        self.fitness_func = fitness_func
        self.size = size
        self.genome_length = genome_length
        self.fitness_limit = fitness_limit
        self.generation_limit = generation_limit

        self.final_population = []
        self.generations = 0

    # Provide a concrete implementation of the abstract `generate` method
    """ Run the genetic algorithm to generate a musical unit """
    def generate(self) -> List[MusicUnit]:
        # Create the initial population
        population = self.generate_population()
        generations = 0
        for i in range(self.generation_limit):
            # Sort the population by fitness
            population = sorted(population,
                                key=lambda binary_gen: self.fitness_func(binary_gen),
                                reverse=True)
            self.print_stats(population, i, self.fitness_func)

            if self.fitness_func(population[0]) >= self.fitness_limit:
                break
            # Create the next generation
            next_generation = population[0:2]

            # Generate offspring
            for j in range(int(len(population) / 2) - 1):
                # Select parents
                parents = selection_pair(population, self.fitness_func)
                # Crossover and mutate to create offspring
                offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
                offspring_a = mutation(offspring_a)
                offspring_b = mutation(offspring_b)
                next_generation += [offspring_a, offspring_b]

            population = next_generation
            generations += 1

        final_population = population

        print("Final PopulationType after %d generations:" % generations)
        for binary_genome in final_population:
            print("%s (Fitness: %d)" % (genome_to_string(binary_genome), self.fitness_func(binary_genome)))

        # Convert best genome to musical unit
        genome = final_population[0]
        unit = binary_to_unit(genome)
        unit.name = 'Genetic ' + str(int(datetime.now().timestamp()))
        return [unit]

    # Generate an initial population of given size and genome length
    def generate_population(self) -> PopulationType:
        return [generate_genome(self.genome_length) for _ in range(self.size)]

    # Sort the population by fitness in descending order
    @staticmethod
    def sort_population(population: PopulationType, fitness_func: FitnessFunctionType) -> PopulationType:
        return sorted(population, key=fitness_func, reverse=True)


    # Print statistics of the current generation
    def print_stats(self, population: PopulationType, generation_id: int, fitness_func: FitnessFunctionType):
        print("GENERATION %02d" % generation_id)
        print("=============")
        print("PopulationType: [%s]" % ", ".join([genome_to_string(gene) for gene in population]))
        print("Avg. Fitness: %f" % (population_fitness(population, fitness_func) / len(population)))
        sorted_population = self.sort_population(population, fitness_func)
        print(
            "Best: %s (%f)" % (genome_to_string(sorted_population[0]), fitness_func(sorted_population[0])))
        print("Worst: %s (%f)" % (genome_to_string(sorted_population[-1]),
                                  fitness_func(sorted_population[-1])))
        print("")

        # Return the best genome (optional) for callers that want it
        return sorted_population[0]

def genome_to_string(genome: GenomeType) -> str:
    """ Convert a genome to a string representation """
    return "".join(map(str, genome))

def single_point_crossover(a: GenomeType, b: GenomeType) -> Tuple[GenomeType, GenomeType]:
    """ Perform single point crossover between two genomes """
    if len(a) != len(b):
        raise ValueError("GenomeTypes a and b must be of same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]

def mutation(genome: GenomeType, num: int = 1, probability: float = 0.5) -> GenomeType:
    """ Mutate a genome by flipping bits at random positions """
    for _ in range(num):
        # Choose a random index in the genome
        index = randrange(len(genome))
        # Flip the bit at the chosen index with a certain probability
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome

def population_fitness(population: PopulationType, fitness_func: FitnessFunctionType) -> int:
    """ Calculate the total fitness of a population """
    return sum([fitness_func(genome) for genome in population])

def generate_genome(length: int) -> GenomeType:
    """ Generate a random genome of given length """
    return choices([0, 1], k=length)

def generate_weighted_distribution(population: PopulationType, fitness_func: FitnessFunctionType) -> PopulationType:
    """Generate a weighted distribution of the population based on fitness"""
    result = []

    for gene in population:
        # Add the gene to the result list a number of times proportional to its fitness
        result += [gene] * int(fitness_func(gene)+1)

    return result

def selection_pair(population: PopulationType, fitness_func: FitnessFunctionType) -> PopulationType:
    """ Select two individuals from the population using a weighted distribution based on fitness"""
    return sample(
        population=generate_weighted_distribution(population, fitness_func),
        k=2
    )

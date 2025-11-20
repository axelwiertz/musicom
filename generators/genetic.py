"""
A simple genetic algorithm implementation in Python.
"""
from datetime import datetime
from random import choices, randint, randrange, random, sample
from typing import List, Callable, Tuple

from structures import MusicUnit, MusicTime
from converters.musicunit import binary_to_unit
from generators import Generator

Genome = List[int]
Population = List[Genome]
FitnessFunc = Callable[[Genome], int]


class GeneticGenerator(Generator):
    # Type aliases for better readability

    # Genetic evolution functions
    def __init__(self, seed_unit: MusicUnit,
                fitness_func: FitnessFunc,
                 size: int,
                 genome_length: int,
                 fitness_limit: int,
                generation_limit: int = 100):
        super().__init__(seed_unit)
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
            population = sorted(population, key=lambda genome: self.fitness_func(genome), reverse=True)
            self.print_stats(population, i, self.fitness_func)

            if self.fitness_func(population[0]) >= self.fitness_limit:
                break
            # Create the next generation
            next_generation = population[0:2]

            # Generate offspring
            for j in range(int(len(population) / 2) - 1):
                # Select parents
                parents = self.selection_pair(population, self.fitness_func)
                # Crossover and mutate to create offspring
                offspring_a, offspring_b = self.single_point_crossover(parents[0], parents[1])
                offspring_a = self.mutation(offspring_a)
                offspring_b = self.mutation(offspring_b)
                next_generation += [offspring_a, offspring_b]

            population = next_generation
            generations += 1

        final_population = population

        print("Final Population after %d generations:" % generations)
        for genome in final_population:
            print("%s (Fitness: %d)" % (self.genome_to_string(genome), self.fitness_func(genome)))

        # Convert best genome to musical unit
        unit = MusicUnit('Genetic ' + str(int(datetime.now().timestamp())))

        genome = final_population[0]

        unit = binary_to_unit(genome)
        return [unit]

    """ Generate a random genome of given length """
    def generate_genome(self, length: int) -> Genome:
        return choices([0, 1], k=length)

    # Generate an initial population of given size and genome length
    def generate_population(self) -> Population:
        return [self.generate_genome(self.genome_length) for _ in range(self.size)]

    # Single point crossover between two genomes
    def single_point_crossover(self, a: Genome, b: Genome) -> Tuple[Genome, Genome]:
        if len(a) != len(b):
            raise ValueError("Genomes a and b must be of same length")

        length = len(a)
        if length < 2:
            return a, b

        p = randint(1, length - 1)
        return a[0:p] + b[p:], b[0:p] + a[p:]

    # Single point crossover
    def mutation(self, genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
        for _ in range(num):
            # Choose a random index in the genome
            index = randrange(len(genome))
            # Flip the bit at the chosen index with a certain probability
            genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
        return genome

    # Calculate the total fitness of a population
    def population_fitness(self, population: Population, fitness_func: FitnessFunc) -> int:
        return sum([fitness_func(genome) for genome in population])

    # Select two individuals from the population using a weighted distribution based on fitness
    def selection_pair(self, population: Population, fitness_func: FitnessFunc) -> Population:
        return sample(
            population=self.generate_weighted_distribution(population, fitness_func),
            k=2
        )

    # Generate a weighted distribution of the population based on fitness
    def generate_weighted_distribution(self, population: Population, fitness_func: FitnessFunc) -> Population:
        result = []

        for gene in population:
            # Add the gene to the result list a number of times proportional to its fitness
            result += [gene] * int(fitness_func(gene)+1)

        return result


    # Sort the population by fitness in descending order
    def sort_population(self, population: Population, fitness_func: FitnessFunc) -> Population:
        return sorted(population, key=fitness_func, reverse=True)

    # Convert a genome to a string representation
    def genome_to_string(self, genome: Genome) -> str:
        return "".join(map(str, genome))

    # Print statistics of the current generation
    def print_stats(self, population: Population, generation_id: int, fitness_func: FitnessFunc):
        print("GENERATION %02d" % generation_id)
        print("=============")
        print("Population: [%s]" % ", ".join([self.genome_to_string(gene) for gene in population]))
        print("Avg. Fitness: %f" % (self.population_fitness(population, fitness_func) / len(population)))
        sorted_population = self.sort_population(population, fitness_func)
        print(
            "Best: %s (%f)" % (self.genome_to_string(sorted_population[0]), fitness_func(sorted_population[0])))
        print("Worst: %s (%f)" % (self.genome_to_string(sorted_population[-1]),
                                  fitness_func(sorted_population[-1])))
        print("")

        # Return the best genome (optional) for callers that want it
        return sorted_population[0]



def create_population():
    # Use a genetic algorithm to create a population of musical units
    time = MusicTime(8, 4, 4, 100)
    unit = MusicUnit("Genetic", time)

    def fitness_func(genome_in: List[int]) -> int:
        # Simple fitness function: sum of genome values
        return sum(genome_in)

    gen = GeneticGenerator(unit, fitness_func=fitness_func, size=10, genome_length=20, fitness_limit=20,
        generation_limit=50)

    # Run the genetic algorithm
    gen.generate()




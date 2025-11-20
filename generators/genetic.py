"""
A simple genetic algorithm implementation in Python.
"""
from datetime import datetime
from random import choices, randint, randrange, random, sample
from typing import List, Optional, Callable, Tuple

from constants import TwelveTET, MIDIinstrument
from structures import MusicComposition, MusicUnit, MusicVoice, MusicTime
from structures.theory import MusicScale,  Diatonic
from generators import Generator

# Type aliases for better readability
Genome = List[int]
Population = List[Genome]
PopulateFunc = Callable[[], Population]
FitnessFunc = Callable[[Genome], int]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]
PrinterFunc = Callable[[Population, int, FitnessFunc], None]



class GeneticGenerator(Generator):
# Genetic evolution functions
    def __init__(self, seed_unit: MusicUnit):
        super().__init__(seed_unit)

    # Generate a random genome of given length
    def generate_genome(self, length: int) -> Genome:
        return choices([0, 1], k=length)

    # Generate an initial population of given size and genome length
    def generate_population(self, size: int, genome_length: int) -> Population:
        return [self.generate_genome(genome_length) for _ in range(size)]

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

        return sorted_population[0]



    # Run the genetic algorithm evolution process
    def run_evolution(self,
            populate_func: PopulateFunc,
            fitness_func: FitnessFunc,
            fitness_limit: int,
            selection_func: SelectionFunc = selection_pair,
            crossover_func: CrossoverFunc = single_point_crossover,
            mutation_func: MutationFunc = mutation,
            generation_limit: int = 100,
            printer: Optional[PrinterFunc] = None) \
            -> Tuple[Population, int]:

        # Create the initial population
        population = populate_func()

        i = 0
        for i in range(generation_limit):
            # Sort the population by fitness
            population = sorted(population, key=lambda genome: fitness_func(genome), reverse=True)

            if printer is not None:
                printer(population, i, fitness_func)

            if fitness_func(population[0]) >= fitness_limit:
                break
            # Create the next generation
            next_generation = population[0:2]

            # Generate offspring
            for j in range(int(len(population) / 2) - 1):
                # Select parents
                parents = selection_func(population, fitness_func)
                # Crossover and mutate to create offspring
                offspring_a, offspring_b = crossover_func(parents[0], parents[1])
                offspring_a = mutation_func(offspring_a)
                offspring_b = mutation_func(offspring_b)
                next_generation += [offspring_a, offspring_b]

            population = next_generation

        return population, i



def create_population():
    # Use a genetic algorithm to create a population of musical units
    time = MusicTime(8, 4, 4, 100)
    unit = MusicUnit("Genetic", time)
    voice = MusicVoice('Genetic voice', [unit], MIDIinstrument.PIANO)
    comp = MusicComposition('Genetic '+str(int(datetime.now().timestamp())),
                             MusicScale(Diatonic.HEPTA, Diatonic.SCALE, TwelveTET.C, Diatonic.major_mode),
                [voice])

    def fitness_func(genome_in: Genome) -> int:
        # Simple fitness function: sum of genome values
        return sum(genome_in)

    # Binary genome representation
    pitch_interval_bits = 6  # binary 24 pitch intervals
    #max_pitch_interval = pow(2, pitch_interval_bits - 1)
    onset_interval_bits = 4  # binary 8 timesteps
    duration_bits = 4  # binary 8 timesteps
    velocity_bits = 4  # binary 8 levels
    totalbits = pitch_interval_bits + duration_bits + onset_interval_bits + velocity_bits

    # Run the genetic algorithm
    gen = GeneticGenerator(unit)
    final_population, generations = gen.run_evolution(
        populate_func=lambda: gen.generate_population(10, 20),
        fitness_func=fitness_func,
        fitness_limit=20,
        generation_limit=50,
        printer=gen.print_stats
    )

    print("Final Population after %d generations:" % generations)
    for genome in final_population:
        print("%s (Fitness: %d)" % (gen.genome_to_string(genome), fitness_func(genome)))

    # Convert best genome to musical unit
    unit = MusicUnit(time)

    genome = final_population[0]
    # Transform a generated genome into a unit
    # Split genome in parts of 'bits' length
    numparts = len(genome) % totalbits
    genes_binary = []
    for i in range(numparts):
        # Extract binary elements
        genes_binary += [genome[(i * totalbits):(i * totalbits) + totalbits]]

    for gene_binary in genes_binary:
        pitch_nr = int(sum([bit * pow(2, i) for i, bit in enumerate(gene_binary)]))

    voice = MusicVoice('Genetic voice', [unit], MIDIinstrument.PIANO)

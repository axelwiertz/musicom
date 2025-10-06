from random import choices, randint, randrange, random, sample
from typing import List, Optional, Callable, Tuple

# Type aliases for better readability
Genome = List[int]
Population = List[Genome]
PopulateFunc = Callable[[], Population]
FitnessFunc = Callable[[Genome], int]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]
PrinterFunc = Callable[[Population, int, FitnessFunc], None]


# Genetic creation

class GeneticCreation:

    def __init__(self,
                 population_size: int,
                 genes_size: int,
                 bits_per_gene: int = 4,
                 ):

        # Population Size   Number of streams per generation to rate and recombine
        self.population_size = population_size
        self.bits_per_gene = bits_per_gene
        self.genes_size = genes_size

        self.genome_size = genes_size * bits_per_gene

        self.genome = Genome()


# Generate a random genome of given length
def generate_genome(length: int) -> Genome:
    return choices([0, 1], k=length)

# Generate an initial population of given size and genome length
def generate_population(size: int, genome_length: int) -> Population:
    return [generate_genome(genome_length) for _ in range(size)]

# Single point crossover between two genomes
def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]

# Single point crossover
def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        # Choose a random index in the genome
        index = randrange(len(genome))
        # Flip the bit at the chosen index with a certain probability
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome

# Calculate the total fitness of a population
def population_fitness(population: Population, fitness_func: FitnessFunc) -> int:
    return sum([fitness_func(genome) for genome in population])

# Select two individuals from the population using a weighted distribution based on fitness
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return sample(
        population=generate_weighted_distribution(population, fitness_func),
        k=2
    )

# Generate a weighted distribution of the population based on fitness
def generate_weighted_distribution(population: Population, fitness_func: FitnessFunc) -> Population:
    result = []

    for gene in population:
        # Add the gene to the result list a number of times proportional to its fitness
        result += [gene] * int(fitness_func(gene)+1)

    return result

# Sort the population by fitness in descending order
def sort_population(population: Population, fitness_func: FitnessFunc) -> Population:
    return sorted(population, key=fitness_func, reverse=True)

# Convert a genome to a string representation
def genome_to_string(genome: Genome) -> str:
    return "".join(map(str, genome))

# Print statistics of the current generation
def print_stats(population: Population, generation_id: int, fitness_func: FitnessFunc):
    print("GENERATION %02d" % generation_id)
    print("=============")
    print("Population: [%s]" % ", ".join([genome_to_string(gene) for gene in population]))
    print("Avg. Fitness: %f" % (population_fitness(population, fitness_func) / len(population)))
    sorted_population = sort_population(population, fitness_func)
    print(
        "Best: %s (%f)" % (genome_to_string(sorted_population[0]), fitness_func(sorted_population[0])))
    print("Worst: %s (%f)" % (genome_to_string(sorted_population[-1]),
                              fitness_func(sorted_population[-1])))
    print("")

    return sorted_population[0]



def evolve (self):
    # Generate populations
    population = generate_population(self.population_size, self.genome_size)

    # Continue with the fittest populations
    population = sort_population (population, fitness_func=FitnessFunc)

    # Three fittest as next population
    next_generation = population[0:2]

    # Generate offspring
    parents = selection_pair(population, FitnessFunc)
    offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])

    #   Number of mutations	    Max number of mutations that should be possible per child generated
    num_mutations: int = 2
    #   Mutation probability
    mutation_probability: float = 0.5

    # Mutate offspring
    offspring_a = mutation(offspring_a, num=num_mutations, probability=mutation_probability)
    offspring_b = mutation(offspring_b, num=num_mutations, probability=mutation_probability)
    next_generation += [offspring_a, offspring_b]


# Run the genetic algorithm evolution process
def run_evolution(
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
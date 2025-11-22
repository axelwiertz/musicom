from itertools import permutations
from typing import List, Tuple

# Helper functions
def sequence_rotations(sequence: List | Tuple) -> List:
    # Generate all rotations of a given sequence
    rotations = [sequence[x:] + sequence[:x] for x in range(len(sequence))]
    return rotations

def interval_to_step(intervals: List[int]) -> List[int]:
    # Convert a list of n intervals to a sequential mask with n+1 sequential degree/onset numbers and zeroes
    # Example [2, 3] -> [1, 0, 2, 0, 0, 3]
    steps = []
    sequence_nr = 1
    for x in intervals:
        steps.append(sequence_nr)
        sequence_nr += 1
        for y in range(1, x):
            steps.append(0)
    return steps

def intervals_to_nodes(intervals: List[int], start_node: int = 0) -> List[int]:
    # Convert a list of (pitch) intervals to (pitch) nodes starting from start_node
    nodes = []
    current_node = start_node
    nodes.append(current_node)
    for itv in intervals:
        current_node += itv
        nodes.append(current_node)
    return nodes

def set_permutations(sequence : List[int]) -> List:
    # Permutations: ordered set of all possible arrangements of the input sequence
    return list(permutations(sequence))

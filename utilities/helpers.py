# Helper functions
def sequence_rotations(sequence: list | tuple) -> list:
    # Generate all rotations of a given sequence
    rotations = [sequence[x:] + sequence[:x] for x in range(len(sequence))]
    return rotations

def interval_to_step(intervals: list[int]) -> list[int]:
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

def intervals_to_nodes(pitch_intervals: List[int], start_pitch_node: int = 0) -> List[int]:
    # Convert a list of pitch intervals to pitch nodes starting from start_pitch_node
    pitch_nodes = []
    current_pitch = start_pitch_node
    pitch_nodes.append(current_pitch)
    for pitch_interval in pitch_intervals:
        current_pitch += pitch_interval
        pitch_nodes.append(current_pitch)
    return pitch_nodes

import random
import string
import itertools
from typing import List

s = string.ascii_lowercase


# Generate something with better good distribution
def random_string() -> str:
    return "".join(random.choice(s) for i in range(8))


# https://stackoverflow.com/questions/52854146/how-to-compute-derangement-permutation-of-a-list-with-repeating-elements
# Slow and possibly always determined
def derangement(iterable) -> List[int]:
    for permutation in itertools.permutations(iterable):
        if not any([a == b for a, b in zip(permutation, iterable)]):
            return zip(iterable, permutation)

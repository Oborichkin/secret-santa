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


TRIES = 100


# https://stackoverflow.com/questions/52854146/how-to-compute-derangement-permutation-of-a-list-with-repeating-elements
# Slow and possibly always determined
def derangement2(iterable: list) -> List[int]:
    for i in range(TRIES):
        senders = iterable.copy()
        receivers = iterable.copy()
        try:
            who_gifts_who = {}
            while senders and receivers:
                sender, receiver = random.choice(senders), random.choice(receivers)
                if sender == receiver:
                    if len(senders) > 1:
                        continue
                    else:
                        raise ValueError("Opps. Gotta start over")
                senders.remove(sender)
                receivers.remove(receiver)
                who_gifts_who[sender] = receiver
            return who_gifts_who
        except ValueError:
            print("stating over...")

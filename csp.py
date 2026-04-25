import random
from utils import subjects

def is_valid(chromo):
    # no same subject continuously
    for i in range(len(chromo)-1):
        if chromo[i] == chromo[i+1]:
            return False
    return True

def repair(chromo):
    n = len(subjects)
    for i in range(len(chromo)-1):
        if chromo[i] == chromo[i+1]:
            chromo[i+1] = random.randint(0, n-1)
    return chromo
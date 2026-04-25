from utils import subjects

def fitness(chromo):
    score = 10   # base score (IMPORTANT)

    # reward diversity
    unique_subjects = len(set(chromo))
    score += unique_subjects * 5

    # penalty for repetition
    for i in range(len(chromo)-1):
        if chromo[i] == chromo[i+1]:
            score -= 5

    return max(score, 1)  # ensure never zero
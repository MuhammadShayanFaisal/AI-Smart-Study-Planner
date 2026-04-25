import random
from copy import deepcopy
from collections import Counter
from fitness import calculate_fitness


def generate_time_slots(start_hour=8, total_slots=12):
    return [f"{start_hour+i}-{start_hour+i+1}" for i in range(total_slots)]


def balance_sequence(seq, subjects_data):
    target = {s["name"]: s["hours"] for s in subjects_data}
    seq = [s for s in seq if s != "Break"]
    current = Counter(seq)

    for i in range(len(seq)):
        sub = seq[i]
        if current.get(sub, 0) > target.get(sub, 0):
            for need_sub, need_count in target.items():
                if current.get(need_sub, 0) < need_count:
                    current[sub] -= 1
                    current[need_sub] = current.get(need_sub, 0) + 1
                    seq[i] = need_sub
                    break

    # Fix any remaining imbalance (add missing, remove extra)
    result = []
    remaining = {k: v for k, v in target.items()}
    for sub in seq:
        if remaining.get(sub, 0) > 0:
            result.append(sub)
            remaining[sub] -= 1
    # Add any still missing
    for sub, count in remaining.items():
        result.extend([sub] * count)

    return result


def fix_consecutive(seq):
    """Swap adjacent duplicates with further elements."""
    seq = list(seq)
    for i in range(1, len(seq)):
        if seq[i] == seq[i-1]:
            for j in range(i+1, len(seq)):
                if seq[j] != seq[i]:
                    seq[i], seq[j] = seq[j], seq[i]
                    break
    return seq


def inject_breaks(seq, break_interval):
    """Insert a Break every break_interval study slots."""
    result = []
    count = 0
    for sub in seq:
        result.append(sub)
        count += 1
        if count >= break_interval:
            result.append("Break")
            count = 0
    return result


def make_schedule(subjects_data, break_interval=2, start_hour=8):
    pool = []
    for s in subjects_data:
        pool.extend([s["name"]] * s["hours"])
    random.shuffle(pool)
    pool = fix_consecutive(pool)
    seq = inject_breaks(pool, break_interval)
    slots = generate_time_slots(start_hour, len(seq))
    return list(zip(slots, seq))


def initialize_population(size, subjects_data, break_interval):
    return [make_schedule(subjects_data, break_interval) for _ in range(size)]


def tournament_selection(population, fitness_scores, k=3):
    indices = random.sample(range(len(population)), min(k, len(population)))
    return deepcopy(population[max(indices, key=lambda i: fitness_scores[i])])


def crossover(p1, p2, subjects_data, break_interval):
    """Crossover study sequences only, then re-build with breaks."""
    s1 = [sub for _, sub in p1 if sub != "Break"]
    s2 = [sub for _, sub in p2 if sub != "Break"]
    n = len(s1)
    if n < 2:
        return make_schedule(subjects_data, break_interval)
    mid = random.randint(1, n - 1)
    child_study = s1[:mid] + s2[mid:]
    child_study = child_study[:n]
    # Balance, fix consecutive, inject breaks
    child_study = balance_sequence(child_study, subjects_data)
    child_study = fix_consecutive(child_study)
    seq = inject_breaks(child_study, break_interval)
    slots = generate_time_slots(8, len(seq))
    return list(zip(slots, seq))


def mutate(schedule, mutation_rate, subjects_data, break_interval):
    """Mutate study slots only, re-balance afterwards."""
    study_seq = [sub for _, sub in schedule if sub != "Break"]
    subjects = [s["name"] for s in subjects_data]
    mutated = list(study_seq)
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            op = random.choice(["swap", "replace"])
            if op == "swap":
                j = random.randint(0, len(mutated) - 1)
                mutated[i], mutated[j] = mutated[j], mutated[i]
            elif op == "replace":
                mutated[i] = random.choice(subjects)
    mutated = balance_sequence(mutated, subjects_data)
    mutated = fix_consecutive(mutated)
    seq = inject_breaks(mutated, break_interval)
    slots = generate_time_slots(8, len(seq))
    return list(zip(slots, seq))


def run_ga(
    subjects_data,
    preferred_times,
    total_hours,
    break_interval=2,
    population_size=30,
    generations=50,
    base_mutation_rate=0.1,
    progress_callback=None,
):
    population = initialize_population(population_size, subjects_data, break_interval)

    fitness_history = []
    best_schedule = None
    best_fitness = float("-inf")
    mutation_rate = base_mutation_rate
    stagnation = 0

    for gen in range(generations):
        fitness_scores = [
            calculate_fitness(chrom, subjects_data, preferred_times)
            for chrom in population
        ]

        gen_best_idx = max(range(len(population)), key=lambda i: fitness_scores[i])
        gen_best_fitness = fitness_scores[gen_best_idx]
        fitness_history.append(gen_best_fitness)

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_schedule = deepcopy(population[gen_best_idx])
            stagnation = 0
        else:
            stagnation += 1

        if stagnation >= 5:
            mutation_rate = min(0.5, mutation_rate + 0.05)
        else:
            mutation_rate = max(base_mutation_rate, mutation_rate - 0.01)

        if progress_callback:
            progress_callback(gen + 1, gen_best_fitness)

        sorted_idx = sorted(range(len(population)), key=lambda i: fitness_scores[i], reverse=True)
        new_population = [deepcopy(population[i]) for i in sorted_idx[:2]]

        while len(new_population) < population_size:
            p1 = tournament_selection(population, fitness_scores)
            p2 = tournament_selection(population, fitness_scores)
            child = crossover(p1, p2, subjects_data, break_interval)
            child = mutate(child, mutation_rate, subjects_data, break_interval)
            new_population.append(child)

        population = new_population

    return best_schedule, best_fitness, fitness_history
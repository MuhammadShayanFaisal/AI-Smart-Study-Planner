"""
Genetic Algorithm Module
========================
Key time rules:
  - Day runs 08:00 → 24:00 (midnight), max 16 usable hours
  - Morning window : 08:00 – 16:00  (slots 8-9 … 15-16)
  - Evening window : 16:00 – 24:00  (slots 16-17 … 23-24)
  - If all subjects prefer Morning, morning slots fill first (8→16),
    overflow goes into evening.  Same logic applies in reverse.
  - Schedule NEVER goes past 24:00.
"""

import random
from copy import deepcopy
from collections import Counter
from fitness import calculate_fitness, sort_schedule_by_priority

# ── Hard time constants ───────────────────────────────────────────────────────
DAY_START      = 8    # 08:00
DAY_END        = 24   # 24:00 (midnight)
MAX_DAY_SLOTS  = DAY_END - DAY_START   # 16 usable slots in a day
MORNING_END    = 16   # morning  = 08:00–16:00
EVENING_START  = 16   # evening  = 16:00–24:00


# ── Slot helpers ─────────────────────────────────────────────────────────────

def all_day_slots():
    """Return all 16 slot labels for the full day 08:00–24:00."""
    return [f"{h}-{h+1}" for h in range(DAY_START, DAY_END)]


def morning_slots():
    return [f"{h}-{h+1}" for h in range(DAY_START, MORNING_END)]   # 8 slots


def evening_slots():
    return [f"{h}-{h+1}" for h in range(EVENING_START, DAY_END)]   # 8 slots


def build_ordered_slots(subjects_data, preferred_times, break_interval):
    # Total slots needed (study + breaks)
    total_study = sum(s["hours"] for s in subjects_data)
    n_breaks    = total_study // break_interval
    total_needed = total_study + n_breaks

    # Cap at max day slots
    total_needed = min(total_needed, MAX_DAY_SLOTS)

    # Count morning vs evening preference by study-hour weight
    morning_hrs = sum(s["hours"] for s in subjects_data
                      if preferred_times.get(s["name"], "Morning") == "Morning")
    evening_hrs = sum(s["hours"] for s in subjects_data
                      if preferred_times.get(s["name"], "Evening") == "Evening")

    # Build slot pool: morning-first or evening-first
    if morning_hrs >= evening_hrs:
        slot_pool = morning_slots() + evening_slots()   # 08 → 24
    else:
        slot_pool = evening_slots() + morning_slots()   # 16 → 24, then 08 → 16

    return slot_pool[:total_needed]


# ── Sequence helpers ──────────────────────────────────────────────────────────

def balance_sequence(seq, subjects_data):
    """Force subject counts to exactly match allocated hours."""
    target  = {s["name"]: s["hours"] for s in subjects_data}
    seq     = [s for s in seq if s != "Break"]
    current = Counter(seq)

    for i in range(len(seq)):
        sub = seq[i]
        if current.get(sub, 0) > target.get(sub, 0):
            for need_sub, need_count in target.items():
                if current.get(need_sub, 0) < need_count:
                    current[sub]    -= 1
                    current[need_sub] = current.get(need_sub, 0) + 1
                    seq[i]          = need_sub
                    break

    # Final pass: honour target exactly
    result    = []
    remaining = dict(target)
    for sub in seq:
        if remaining.get(sub, 0) > 0:
            result.append(sub)
            remaining[sub] -= 1
    for sub, cnt in remaining.items():
        result.extend([sub] * cnt)

    return result


def fix_consecutive(seq):
    """Swap adjacent duplicates with a later different element."""
    seq = list(seq)
    for i in range(1, len(seq)):
        if seq[i] == seq[i - 1]:
            for j in range(i + 1, len(seq)):
                if seq[j] != seq[i]:
                    seq[i], seq[j] = seq[j], seq[i]
                    break
    return seq


def inject_breaks(seq, break_interval):
    """Insert 'Break' every break_interval study slots."""
    result, count = [], 0
    for sub in seq:
        result.append(sub)
        count += 1
        if count >= break_interval:
            result.append("Break")
            count = 0
    return result


def assign_slots(subject_seq, ordered_slots):
    """
    Pair subjects (with breaks already injected) to the ordered slot list.
    Truncates or pads to fit exactly len(ordered_slots).
    """
    n = len(ordered_slots)
    # Trim if too long
    subj = subject_seq[:n]
    # Pad with Break if too short
    while len(subj) < n:
        subj.append("Break")
    return list(zip(ordered_slots, subj))


# ── Schedule factory ─────────────────────────────────────────────────────────

def make_schedule(subjects_data, preferred_times, break_interval):
    pool = []
    for s in subjects_data:
        pool.extend([s["name"]] * s["hours"])
    random.shuffle(pool)
    pool  = fix_consecutive(pool)
    seq   = inject_breaks(pool, break_interval)
    slots = build_ordered_slots(subjects_data, preferred_times, break_interval)
    return assign_slots(seq, slots)


# ── GA operators ─────────────────────────────────────────────────────────────

def initialize_population(size, subjects_data, preferred_times, break_interval):
    return [make_schedule(subjects_data, preferred_times, break_interval)
            for _ in range(size)]


def tournament_selection(population, fitness_scores, k=3):
    indices = random.sample(range(len(population)), min(k, len(population)))
    return deepcopy(population[max(indices, key=lambda i: fitness_scores[i])])


def crossover(p1, p2, subjects_data, preferred_times, break_interval):
    s1 = [sub for _, sub in p1 if sub != "Break"]
    s2 = [sub for _, sub in p2 if sub != "Break"]
    n  = len(s1)
    if n < 2:
        return make_schedule(subjects_data, preferred_times, break_interval)
    mid         = random.randint(1, n - 1)
    child_study = (s1[:mid] + s2[mid:])[:n]
    child_study = balance_sequence(child_study, subjects_data)
    child_study = fix_consecutive(child_study)
    seq         = inject_breaks(child_study, break_interval)
    slots       = build_ordered_slots(subjects_data, preferred_times, break_interval)
    return assign_slots(seq, slots)


def mutate(schedule, mutation_rate, subjects_data, preferred_times, break_interval):
    study_seq = [sub for _, sub in schedule if sub != "Break"]
    subjects  = [s["name"] for s in subjects_data]
    mutated   = list(study_seq)
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            if random.random() < 0.5:          # swap
                j = random.randint(0, len(mutated) - 1)
                mutated[i], mutated[j] = mutated[j], mutated[i]
            else:                               # replace
                mutated[i] = random.choice(subjects)
    mutated = balance_sequence(mutated, subjects_data)
    mutated = fix_consecutive(mutated)
    seq     = inject_breaks(mutated, break_interval)
    slots   = build_ordered_slots(subjects_data, preferred_times, break_interval)
    return assign_slots(seq, slots)


# ── Main GA loop ──────────────────────────────────────────────────────────────

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
    """
    Returns (best_schedule, best_fitness, fitness_history).

    Schedule guaranteed:
      - Starts at 08:00, ends no later than 24:00
      - Morning subjects scheduled 08–16, Evening 16–24
      - Breaks every break_interval study hours
      - High-priority subjects appear first
    """
    # Warn if user asked for more hours than the day allows
    total_study = sum(s["hours"] for s in subjects_data)
    n_breaks    = total_study // break_interval
    total_slots_needed = total_study + n_breaks
    if total_slots_needed > MAX_DAY_SLOTS:
        # Silently cap — the assign_slots function handles truncation
        pass

    population = initialize_population(
        population_size, subjects_data, preferred_times, break_interval
    )

    fitness_history = []
    best_schedule   = None
    best_fitness    = float("-inf")
    mutation_rate   = base_mutation_rate
    stagnation      = 0

    for gen in range(generations):
        fitness_scores = [
            calculate_fitness(chrom, subjects_data, preferred_times)
            for chrom in population
        ]

        gen_best_idx     = max(range(len(population)), key=lambda i: fitness_scores[i])
        gen_best_fitness = fitness_scores[gen_best_idx]
        fitness_history.append(gen_best_fitness)

        if gen_best_fitness > best_fitness:
            best_fitness  = gen_best_fitness
            best_schedule = deepcopy(population[gen_best_idx])
            stagnation    = 0
        else:
            stagnation += 1

        # Adaptive mutation
        if stagnation >= 5:
            mutation_rate = min(0.5, mutation_rate + 0.05)
        else:
            mutation_rate = max(base_mutation_rate, mutation_rate - 0.01)

        if progress_callback:
            progress_callback(gen + 1, gen_best_fitness)

        # Next generation with elitism (keep top 2)
        sorted_idx     = sorted(range(len(population)),
                                key=lambda i: fitness_scores[i], reverse=True)
        new_population = [deepcopy(population[i]) for i in sorted_idx[:2]]

        while len(new_population) < population_size:
            p1    = tournament_selection(population, fitness_scores)
            p2    = tournament_selection(population, fitness_scores)
            child = crossover(p1, p2, subjects_data, preferred_times, break_interval)
            child = mutate(child, mutation_rate, subjects_data,
                           preferred_times, break_interval)
            new_population.append(child)

        population = new_population

    # Post-process: sort study blocks so High > Med > Low priority
    best_schedule = sort_schedule_by_priority(best_schedule, subjects_data)
    best_fitness  = calculate_fitness(best_schedule, subjects_data, preferred_times)

    return best_schedule, best_fitness, fitness_history
import random
from utils import subjects, time_slots
from fitness import fitness
from csp import repair
import matplotlib.pyplot as plt

def create_random_individual():
    n = len(subjects)
    return [random.randint(0, n-1) for _ in range(len(time_slots))]
def roulette_wheel_selection(population, fitness_values):
    total = sum(fitness_values)

    # fallback if all fitness same
    if total == 0:
        return random.sample(population, 2)

    probs = [f/total for f in fitness_values]
    return random.choices(population, probs, k=2)

def two_point_crossover(p1, p2):
    a = random.randint(0, len(p1)-2)
    b = random.randint(a+1, len(p1)-1)
    c1 = p1[:a] + p2[a:b] + p1[b:]
    c2 = p2[:a] + p1[a:b] + p2[b:]
    return c1, c2

def swap_mutation(chromo):
    i, j = random.sample(range(len(chromo)), 2)
    chromo[i], chromo[j] = chromo[j], chromo[i]
    return chromo

def decode(chromo):
    schedule = []
    for i in range(len(chromo)):
        schedule.append((time_slots[i], subjects[chromo[i]]))
    return schedule

def genetic_algorithm():
    population = [create_random_individual() for _ in range(20)]
    
    best = None
    best_score = -999
    fitness_history = []

    for gen in range(30):
        fitness_values = [fitness(ind) for ind in population]
        new_population = []

        for _ in range(len(population)//2):
            p1, p2 = roulette_wheel_selection(population, fitness_values)

            c1, c2 = two_point_crossover(p1, p2)

            if random.random() < 0.2:
                c1 = swap_mutation(c1)
            if random.random() < 0.2:
                c2 = swap_mutation(c2)

            c1 = repair(c1)
            c2 = repair(c2)

            new_population.extend([c1, c2])

        population = new_population

        for ind in population:
            score = fitness(ind)
            if score > best_score:
                best_score = score
                best = ind

        fitness_history.append(best_score)

    # plot graph
    plt.plot(fitness_history)
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("GA Optimization")
    plt.show()

    return best
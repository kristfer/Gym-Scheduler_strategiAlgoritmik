import random
from copy import deepcopy
from greedy import greedy_algorithm

# =============== GENETIC ALGORITHM FOR WORKOUT SCHEDULING ===============

def fitness(schedule, availability):
    """
    Calculate fitness score for a schedule
    Higher score = better schedule
    """
    score = 0
    for day, workouts in schedule.items():
        total_duration = sum(w['duration'] for w in workouts)
        available_time = availability.get(day, 0)
        
        # Penalty for exceeding available time
        if total_duration > available_time:
            score -= (total_duration - available_time) * 10
        else:
            # Reward for using available time efficiently
            score += total_duration * 5
            
        # Bonus for balanced schedule
        if 0.5 <= total_duration <= available_time:
            score += 2
            
    return score

def generate_population(base_schedule, population_size=20):
    """Generate initial population from base schedule"""
    population = []
    days = list(base_schedule.keys())
    
    for _ in range(population_size):
        individual = {}
        for day in days:
            workouts = [w.copy() for w in base_schedule[day]]
            random.shuffle(workouts)
            individual[day] = workouts
        population.append(individual)
    return population

def crossover(parent1, parent2):
    """Create child by combining two parents"""
    child = {}
    days = list(parent1.keys())
    split = random.randint(1, len(days) - 2)
    
    for i, day in enumerate(days):
        if i < split:
            child[day] = [w.copy() for w in parent1[day]]
        else:
            child[day] = [w.copy() for w in parent2[day]]
    return child

def mutate(individual, workouts, mutation_rate=0.2):
    """Randomly modify individual by swapping workouts"""
    days = list(individual.keys())
    active_workouts = [w for w in workouts if w['type'] != 'rest']
    
    for day in days:
        if random.random() < mutation_rate and individual[day]:
            # Only mutate active workout days
            if individual[day] and individual[day][0]['type'] != 'rest':
                idx = random.randint(0, len(individual[day]) - 1)
                current_names = [w['name'] for w in individual[day]]
                candidates = [w for w in active_workouts if w['name'] not in current_names]
                if candidates:
                    individual[day][idx] = random.choice(candidates).copy()

def genetic_algorithm(workouts, availability, generations=30, population_size=20, base_schedule=None):
    """
    Main genetic algorithm function
    Evolves workout schedules over multiple generations
    """
    # Start with provided base schedule or greedy solution
    if base_schedule is None:
        base_schedule = greedy_algorithm(workouts, availability)
    else:
        base_schedule = base_schedule
    
    # Generate initial population
    population = generate_population(base_schedule, population_size)

    # Evolution loop
    for generation in range(generations):
        # Sort by fitness (best first)
        population.sort(key=lambda indiv: fitness(indiv, availability), reverse=True)
        
        # Elitism - keep best 2 individuals
        new_pop = [deepcopy(population[0]), deepcopy(population[1])]
        
        # Generate new individuals through crossover and mutation
        while len(new_pop) < population_size:
            parent1, parent2 = random.sample(population[:max(2, population_size//2)], 2)
            child = crossover(parent1, parent2)
            mutate(child, workouts)
            new_pop.append(child)
            
        population = new_pop

    # Return best individual
    population.sort(key=lambda indiv: fitness(indiv, availability), reverse=True)
    return population[0]
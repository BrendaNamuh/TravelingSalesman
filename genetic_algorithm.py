import math
import random 
import requests 

# Input : Number of locations user would like to visit
# Ouput: list of potential paths to visit all locations 
def generate_random_paths(nmbr_destinations):
    random_paths = []
    for _ in range(1, 20000):
        path = list(range(1,nmbr_destinations))
        random.shuffle(path)
        random_path = [0] +path
        random_paths.append(random_path)
    print(f'Random paths generated:{random_paths}')
    return random_paths



def total_distance(points, path):
    origin = 'H7N 0C4'
    destination = 'H7S 1Y9'
    response = requests.get(f"https://maps.googleapis.com/maps/api/distancematrix/json?destinations={destination}&origins={origin}&units=imperial&key={GOOGLE_API_KEY}")
    response = response.json()
    print('Response:', response)
    seconds = response['rows'][0]['elements'][0]['duration']['value']
    print(seconds)
    return sum(math.dist(points[path[i - 1]], points[path[i]]) for i in range(len(path)))


def choose_survivors(points, old_generation):
    survivors = []
    random.shuffle(old_generation)
    midway = len(old_generation) // 2
    for i in range(midway):
        if total_distance(points, old_generation[i]) < total_distance(points, old_generation[i + midway]):
            survivors.append(old_generation[i])
        else:
            survivors.append(old_generation[i + midway])
    print(f'These are the survivors: {survivors}')
    return survivors


def create_offspring(parent_a, parent_b):
    offspring = []
    start = random.randint(0, len(parent_a) - 1)
    finish = random.randint(start, len(parent_a))
    sub_path_from_a = parent_a[start:finish]
    remaining_path_from_b = list([item for item in parent_b if item not in sub_path_from_a])
    for i in range(0, len(parent_a)):
        if start <= i < finish:
            offspring.append(sub_path_from_a.pop(0))
        else:
            offspring.append(remaining_path_from_b.pop(0))
    return offspring


def apply_crossovers(survivors):
    offsprings = []
    midway = len(survivors) // 2
    for i in range(midway):
        parent_a, parent_b = survivors[i], survivors[i + midway]
        for _ in range(2):
            offsprings.append(create_offspring(parent_a, parent_b))
            offsprings.append(create_offspring(parent_b, parent_a))
    return offsprings


def apply_mutations(generation):
    gen_wt_mutations = []
    for path in generation:
        if random.randint(0, 1000) < 9:
            index1, index2 = random.randint(1, len(path) - 1), random.randint(1, len(path) - 1)
            path[index1], path[index2] = path[index2], path[index1]
        gen_wt_mutations.append(path)
    return gen_wt_mutations


def generate_new_population(points, old_generation):
    survivors = choose_survivors(points, old_generation)
    crossovers = apply_crossovers(survivors)
    new_population = apply_mutations(crossovers)
    return new_population


def choose_best(points, paths, count):

    sorted_path_distances = sorted(paths, key=lambda path: total_distance(points, path))
    print("Points: ", points)
    print("Paths: ", paths)
    print("Sorted Path distances: ", sorted_path_distances)
    return sorted_path_distances[:count]


def choose_worst(points, paths, count):
    return sorted(paths, reverse=True, key=lambda path: total_distance(points, path))[:count]


def choose_random(paths, count):
    return [random.choice(paths) for _ in range(count)]

def run_gen_algo(points):
    # Generate initial random paths
    num_destinations = len(points)
    population = generate_random_paths(num_destinations)
    
    # Run the genetic algorithm for some generations
    generations = 1000
    for _ in range(generations):
        population = generate_new_population(points, population)

    # Choose the best path from the final population
    best_path = choose_best(points, population, 1)[0]

    # Print the best path and its distance
    print("Best path:", best_path)
    print("Total distance:", total_distance(points, best_path))
    return best_path




if __name__ == '__main__':
    print('Determining Best Path Using Genetic Algorithem ...')
    
    # Example list of coordinates (x, y)
    points = [[0, 0], [1, 2], [3, 1], [4, 4], [5, 6]]
    run_gen_algo(points)
    
    

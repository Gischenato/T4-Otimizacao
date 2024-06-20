from KDTree import KDTree, distance as get_distance, get_lowest_path_with_kdtree_greedy
import random
import heapq
import time
import sys

FILE = sys.argv[1] if len(sys.argv) > 1 else 'data.txt'

print(FILE)

POPULATION_SIZE = 1
SAMPLE_SIZE = 0 # 0 to use all cities

# Cross over quantity
CROSS_OVER_QUANTITY = 2

# Greedy path cross over quantity
GREEDY_PATH_CROSS_OVER_QUANTITY = 0

# Quantity of paths to mutate (X times each path) randomly 
RANDOM_MUTATION_QUANTITY = 3

# Quantity of paths to mutate (X times each path) with nearest neighbor
NEAREST_PATH_MUTATION_QUANTITY = 4
# Max k (greedy path size) for nearest neighbor mutation
MAX_K = 300

# Skip generations to print
SKIP = 1

# Time out in seconds to print
TIME_OUT = 10
LOG_TIME_OUT = False

TIME_IT = False


CIDADES = []
CURR_BEST_PATH = None
KD_Tree = KDTree()
START = time.time()
PROBS = []

with open(FILE) as f:
    next(f)
    for line in f:
        x, y, label = line.strip().split(' ')
        CIDADES.append((float(x), float(y), label))

    if SAMPLE_SIZE > len(CIDADES) or SAMPLE_SIZE == 0:
        SAMPLE_SIZE = len(CIDADES)
        
    CIDADES = random.sample(CIDADES, SAMPLE_SIZE)

    if MAX_K > len(CIDADES):
        MAX_K = len(CIDADES) - len(CIDADES) // 10
        
        
    tot_before_selection = POPULATION_SIZE + RANDOM_MUTATION_QUANTITY + NEAREST_PATH_MUTATION_QUANTITY + GREEDY_PATH_CROSS_OVER_QUANTITY    
    if CROSS_OVER_QUANTITY > tot_before_selection:
        CROSS_OVER_QUANTITY = tot_before_selection // 2

    if POPULATION_SIZE > SAMPLE_SIZE:
        POPULATION_SIZE = SAMPLE_SIZE

    KD_Tree.insert_list(CIDADES)
    print(KD_Tree)


def timeit(func):
    global TIME_IT
    import time
    def wrapper(*args, **kwargs):
        if not TIME_IT:
            return func(*args, **kwargs)
        start = time.time()
        result = func(*args, **kwargs)
        print(f'{func.__name__} took {time.time() - start} seconds')
        return result
    return wrapper

def path_cost(path):
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += get_distance(path[i], path[i + 1])
    total_distance += get_distance(path[-1], path[0])
    return total_distance

def crossover(parent1, parent2):
    parent1 = parent1[1]
    parent2 = parent2[1]
    size = len(parent1)
    
    p1, p2 = sorted(random.sample(range(size//10), 2))
    p2 += 1

    child = [None] * size
    child[p1:p2] = parent1[p1:p2]
    
    already_in_child = set(child[p1:p2])
    remaining = [city for city in parent2 if city not in already_in_child]
    
    current_pos = p2 % size
    for i in range(p2, p2+size):
        city = parent2[i % size]
        if city not in already_in_child:
            child[current_pos] = city
            current_pos = (current_pos + 1) % size
            remaining.remove(city)
        if len(remaining) == 0:
            break
    path_distance = path_cost(child)
    return (-path_distance, child)

@timeit
def make_cross_overs(population):
    new_population = []
    for i in range(0, CROSS_OVER_QUANTITY, 2):
        if i + 1 == len(population):
            break
        new_population.append(crossover(population[i], population[i + 1]))
    return new_population

def mutation(path):
    path = path[1].copy()
    p1, p2 = random.sample(range(len(path)), 2)
    
    path[p1], path[p2] = path[p2], path[p1]
    
    path_distance = path_cost(path)
    
    return (-path_distance, path)

@timeit
def make_mutations(population):
    new_population = []
    to_mutate = random.sample(range(len(population)), len(population))
    
    for pos in to_mutate:
        for i in range(RANDOM_MUTATION_QUANTITY):
            new_population.append(mutation(population[pos]))
    
    return new_population


def mutate_nearest_neighbor(path, k=1):
    path = path[1].copy()
    p1 = random.randint(0, len(path) - 1 - k)
    exclude_labels = {path[p1][2]}
    for _ in range(k):
        p2 = KD_Tree.nearest_neighbor(path[p1], exclude_labels=exclude_labels)
        p2 = path.index(p2)
        # print(p1, p2)
        path[p1+1], path[p2] = path[p2], path[p1+1]
        p1 = p1 + 1
        exclude_labels.add(path[p1][2])
    
    path_distance = path_cost(path)
    return (-path_distance, path)

@timeit
def make_mutations_nearest_neighbor(population):
    new_population = []
    to_mutate = random.sample(range(len(population)), len(population))
    # print(to_mutate)
    for pos in to_mutate:
        for _ in range(NEAREST_PATH_MUTATION_QUANTITY):
            k = random.randint(1, MAX_K)
            new_population.append(mutate_nearest_neighbor(population[pos], k))
    return new_population

@timeit
def selection(population):
    # print('--- SELECTION ---')
    # print(len(population))
    heapq.heapify(population)
    while len(population) > POPULATION_SIZE:
        heapq.heappop(population)

def get_random_path(cities):
    cities = cities.copy()
    random.shuffle(cities)
    return cities

def make_random_population(n):
    new_population = []
    for i in range(n):
        random_path = get_random_path(CIDADES)
        cost = path_cost(random_path)
        new_population.append((-cost, random_path))
    return new_population

def greedy_crossover(parent2):
    # print('--- Testing ---')
    path, cost = get_lowest_path_with_kdtree_greedy(CIDADES, KD_Tree, random.randint(0, len(CIDADES) - 1))
    greedy_path = (-cost, path)
    # print(parent2)
    # print(greedy_path)
    new_path = crossover(greedy_path, parent2)
    return new_path

@timeit
def make_greedy_crossover(population):
    new_population = []
    for _ in range(GREEDY_PATH_CROSS_OVER_QUANTITY):
        parent2 = random.choice(population)
        new_population.append(greedy_crossover(parent2))
    return new_population

@timeit
def generate_population():
    population = []
    print('Generating Population')
    curr = 0
    for i in random.sample(range(len(CIDADES)), POPULATION_SIZE):
        print(curr)
        curr += 1
        # path, cost = get_lowest_path_with_kdtree_greedy(CIDADES, KD_Tree, start=i)
        path = get_random_path(CIDADES)
        cost = path_cost(path)
        population.append((-cost, path)) 
    
    return population



def genetic_algorithm():
    global START, CURR_BEST_PATH
    last = 0
    population = generate_population()
    timer_acc = time.time()

    for gen in range(100000000000000):
        selection(population)
        
        population += make_mutations(population)
        # population += make_random_population(4)
        population += make_mutations_nearest_neighbor(population)
        population += make_greedy_crossover(population)
        population += make_cross_overs(population)
        population += make_mutations(population)
        
        current = max(population, key=lambda val: val[0])[0]
        
        if time.time() - timer_acc > TIME_OUT:
            timer_acc = time.time()
            yield None, current, gen
        
        if current != last and gen % SKIP == 0:
            last = current
            CURR_BEST_PATH = max(population, key=lambda val: val[0])[1]
            yield CURR_BEST_PATH, current, gen
            
        


def main():

    try:

        for n, x in enumerate(genetic_algorithm()):
            if x[0] is None:
                if LOG_TIME_OUT:
                    print(x[1], f'{(time.time() - START)/60:.2f}min  {x[2]}gen')
                continue
            
            path, cost, gen = x
            print(f'| Cost: {-cost:.2f} | Gen: {gen} | Time: {(time.time() - START)/60:.2f}min | -> Caminho melhorado {n+1}x ')
            pass
        
    except KeyboardInterrupt:
        print('--- KeyboardInterrupt ---')
        pass
    finally:
        # print(f'--- Best Path ---')
        # print(CURR_BEST_PATH)
        pass


if __name__ == '__main__':
    main()

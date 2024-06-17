from KDTree import KDTree, distance as get_distance, get_lowest_path_with_kdtree_greedy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import heapq

CIDADES = []
POPULATION_SIZE = 30

KD_Tree = KDTree()

with open('data.txt') as f:
    next(f)
    for line in f:
        x, y, label = line.strip().split(' ')
        CIDADES.append((float(x), float(y), label))

    CIDADES = random.sample(CIDADES, 2000)

    KD_Tree.insert_list(CIDADES)
    print(KD_Tree)


def plot_population(population):
    x_coords = [point[0] for point in population]
    y_coords = [point[1] for point in population]
    labels = [point[2] for point in population]

    plt.clf()  # Clear the current figure
    plt.scatter(x_coords, y_coords, color='blue', s=10)
    for i in range(len(population) - 1):
        plt.annotate('', xy=(x_coords[i + 1], y_coords[i + 1]), xytext=(x_coords[i], y_coords[i]),
                     arrowprops=dict(arrowstyle="->", lw=0.7, color='red'))

    plt.annotate('', xy=(x_coords[0], y_coords[0]), xytext=(x_coords[-1], y_coords[-1]),
                 arrowprops=dict(arrowstyle="->", lw=0.7, color='blue'))
        

    plt.gca().invert_yaxis()

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'Gráfico de Pontos com Conexões')
    plt.grid(False)

def timeit(func):
    import time
    def wrapper(*args, **kwargs):
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
    
    p1, p2 = sorted(random.sample(range(size), 2))
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

# @timeit
def make_cross_overs(population):
    new_population = []
    for i in range(0, len(population), 2):
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

# @timeit
def make_mutations(population):
    new_population = []
    # create mutations for 10% of the population
    to_mutate = random.sample(range(len(population)), len(population) // 10)
    
    for pos in  to_mutate:
        new_population.append(mutation(population[pos]))
    
    return new_population

def selection(population):
    # print('--- SELECTION ---')
    # print(len(population))
    # print(POPULATION_SIZE)
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

def test(parent2):
    # print('--- Testing ---')
    path, cost = get_lowest_path_with_kdtree_greedy(CIDADES, KD_Tree, random.randint(0, len(CIDADES) - 1))
    greedy_path = (-cost, path)
    # print(parent2)
    # print(greedy_path)
    new_path = crossover(greedy_path, parent2)
    return new_path

# @timeit
def make_test(population, n):
    # get n paths from the population randomly
    new_population = []
    for i in range(n):
        parent2 = random.choice(population)
        new_population.append(test(parent2))
    return new_population

def generate_population():
    population = []
    print('Generating Population')
    for i in random.sample(range(len(CIDADES)), POPULATION_SIZE):
        # path, cost = get_lowest_path_with_kdtree_greedy(CIDADES, KD_Tree, start=i)
        path = get_random_path(CIDADES)
        cost = path_cost(path)
        population.append((-cost, path)) 
    
    return population



import multiprocessing as mp
def genetic_algorithm():
    last = 0
    population = generate_population()
        
    for i in range(100000000000000):
        selection(population)
        
        new_population_1 =  make_mutations(population)
        new_population_2 =  make_random_population(4)
        new_population_3 =  make_test(population, 1)
        new_population_4 =  make_cross_overs(population)
        new_population_5 =  make_mutations(population)
        
        population = population + new_population_1 + new_population_3 + new_population_4 + new_population_5
        # print(population)
        # print(max(population, key=lambda val: val[0])[0])
        current = max(population, key=lambda val: val[0])[0]
        minu = min(population, key=lambda val: val[0])[0]
        if i % 10 == 0:
            print(i)
            print(int(current), int(minu))
        if current != last:
            print(current)
            last = current
            
        


def main():
    genetic_algorithm()
    # only_names = lambda val: val[2]
    # population = generate_population()
    # p1, p2 = population[0], population[1]
    # print(list(map(only_names, p1[1])))
    
    # print(list(map(only_names, p2[1])))
    
    # p3 = crossover(p1, p2)
    # print(list(map(only_names, p3[1])))
    
    
    pass


if __name__ == '__main__':
    main()

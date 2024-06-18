from KDTree import KDTree, distance as get_distance, get_lowest_path_with_kdtree_greedy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
import random
import heapq
import time
import sys
import imageio

CIDADES = []
POPULATION_SIZE = 4
SAMPLE_SIZE = 2000

PLOT = True

MAX_K = 120

CROSS_OVER_QUANTITY = 10
MUTATION_QUANTITY = 10

SKIP = 1

KD_Tree = KDTree()

START = time.time()


CURR_BEST_PATH = None

with open('data.txt') as f:
    next(f)
    for line in f:
        x, y, label = line.strip().split(' ')
        CIDADES.append((float(x), float(y), label))

    if SAMPLE_SIZE > len(CIDADES):
        SAMPLE_SIZE = len(CIDADES)
    if MAX_K > len(CIDADES):
        MAX_K = len(CIDADES)

    CIDADES = random.sample(CIDADES, SAMPLE_SIZE)
    
    with open('result.txt', 'w') as f:
        for x, y, label in CIDADES:
            f.write(f'{x} {y} {label}\n')

    KD_Tree.insert_list(CIDADES)
    print(KD_Tree)


def plot_population(population, gen=0, best_cost=0):
    x_coords = [point[0] for point in population]
    y_coords = [point[1] for point in population]

    plt.clf()  # Clear the current figure
    plt.scatter(x_coords, y_coords, color='blue', s=5)

    # Create line segments for faster plotting, excluding labels
    segments = [((x_coords[i], y_coords[i]), (x_coords[i + 1], y_coords[i + 1])) for i in range(len(population) - 1)]
    segments.append(((x_coords[-1], y_coords[-1]), (x_coords[0], y_coords[0])))  # Close the loop

    line_segments = LineCollection(segments, color='red', linewidths=0.7, linestyle='-')
    plt.gca().add_collection(line_segments)

    plt.gca().invert_yaxis()
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'\nTraveling Salesman Problem\nGenetic Algorithm\nGen: {gen}\nBest Cost: {best_cost:.2f}\nTime: {time.time() - START:.0f} seconds')
    plt.grid(False)

    plt.draw()


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
    for i in range(0, len(population), 2*2):
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
    to_mutate = random.sample(range(len(population)), len(population))
    
    for pos in  to_mutate:
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

def make_mutations_nearest_neighbor(population):
    new_population = []
    to_mutate = random.sample(range(len(population)), len(population))
    # print(to_mutate)
    for pos in to_mutate:
        for _ in range(MUTATION_QUANTITY):
            k = random.randint(1, MAX_K)
            new_population.append(mutate_nearest_neighbor(population[pos], k))
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



def genetic_algorithm():
    global START, CURR_BEST_PATH
    last = 0
    population = generate_population()
    timer_acc = time.time()

    for gen in range(100000000000000):
        selection(population)
        
        population += make_mutations(population)
        # population += make_random_population(4)
        # population += make_test(population, 1)
        population += make_mutations_nearest_neighbor(population)
        population += make_cross_overs(population)
        population += make_mutations(population)
        
        current = max(population, key=lambda val: val[0])[0]
        minu = min(population, key=lambda val: val[0])[0]
        
        if time.time() - timer_acc > 2:
            timer_acc = time.time()
            yield None, current, gen
        
        if current != last and gen % SKIP == 0:
            print('--- YIELD ---')
            print(current)
            last = current
            # print('=============')
            CURR_BEST_PATH = max(population, key=lambda val: val[0])[1]
            yield CURR_BEST_PATH, current, gen
            
        


def main():
    
    print_time = time.time()
    
    if PLOT:
        fig = plt.figure(figsize=(10, 8))
        fig.canvas.manager.window.wm_geometry("+0+0")
        fig.canvas.manager.window.wm_geometry(f"-{3000}+0")

    frames = []
    
    def update(frame):
        nonlocal print_time, frames
        
        if frame[0] is None:
            if time.time() - print_time > 10:
                print_time = time.time()
                print(frame[1], f'{(time.time() - START)/60:.2f}min  {frame[2]}gen')
            return
        plot_population(frame[0], gen=frame[2], best_cost=frame[1])
        
        plt.savefig('plot.png')
        frames.append(imageio.imread('plot.png'))
    
    try:
        if PLOT:
            ani = animation.FuncAnimation(fig, update, frames=genetic_algorithm(), repeat=False, interval=200)
            plt.show()
        else:
            for x in genetic_algorithm():
                pass
        
    except:
        pass
    finally:
        with open('result.txt', 'w') as f:
            for x, y, label in CURR_BEST_PATH:
                f.write(f'{x} {y} {label}\n')
        imageio.mimsave('result.gif', frames, duration=0.2)


if __name__ == '__main__':
    main()

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import random

CIDADES = []
POPULATION = 16
HALF_POPULATION = int(POPULATION/2)
with open('data.txt') as data:
    next(data)
    for line in data:
        x,y,name = line.strip().split()
        CIDADES.append((float(x),float(y),name))

    CIDADES = random.sample(CIDADES, 200)
        
        
def get_distance(c1, c2):
    x1, y1, _ = c1
    x2, y2, _ = c2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def get_path_distance(path):
    tot = sum([get_distance(path[i], path[i+1]) for i in range(len(path) - 1)])
    tot += get_distance(path[0], path[-1])
    return tot

def get_lowest_path_greedy(cities):
    start = random.randint(0, len(cities) - 1)
    cities = cities.copy()
    path = [cities.pop(start)]
    while cities:
        if len(cities) % 100 == 0: print(len(cities))
        last_city = path[-1]
        next_city = min(cities, key=lambda city: get_distance(last_city, city))
        path.append(cities.pop(cities.index(next_city)))
    return path

def get_random_path(cities):
    cities = cities.copy()
    random.shuffle(cities)
    return cities

def plot_population(population):
    x_coords = [point[0] for point in population]
    y_coords = [point[1] for point in population]
    labels = [point[2] for point in population]
    
    plt.figure(figsize=(10, 8))
    plt.scatter(x_coords, y_coords, color='blue', s=10)
    for i in range(len(population) - 1):
        plt.annotate('', xy=(x_coords[i+1], y_coords[i+1]), xytext=(x_coords[i], y_coords[i]),
                     arrowprops=dict(arrowstyle="->", lw=0.3, color='red'))
    # for x, y, label in population:
    #     plt.text(x, y, label, fontsize=9, ha='right')
    plt.gca().invert_yaxis()

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'Gráfico de Pontos com Conexões')
    plt.grid(True)
    plt.show()



def mutate(path):
    i, j = random.sample(range(len(path)), 2)
    path[i], path[j] = path[j], path[i]
    return path

def crossover(path1, path2):
    i, j = random.sample(range(len(path1)), 2)
    if i > j:
        i, j = j, i
    new_path = path1[i:j]
    for city in path2:
        if city not in new_path:
            new_path.append(city)
    return new_path

def fitness(path):
    return get_path_distance(path)

def selection(population):
    population.sort(key=lambda path: fitness(path))
    return population[:HALF_POPULATION]
    
GENERATIONS = 10000000

def genetic_algorithm(population):
    for i in range(GENERATIONS):
        # if i % 1000 == 0: print(i, fitness(population[0]))
        print(i, fitness(population[0]))
        # print(list(map(lambda x: fitness(x), population)))
        new_population = []
        for _ in range(HALF_POPULATION):
            path1, path2 = random.sample(population, 2)
            new_population.append(mutate(crossover(path1, path2)))
            
            # plot_population(ax, population)
            # plt.show()
        population = selection(population + new_population)
    return population[0]
    

def main():
    population = []
    # for _ in range(POPULATION):
    #     population.append(get_lowest_path_greedy(CIDADES))
    for _ in range(POPULATION):
        population.append(get_random_path(CIDADES))
    
    try:
        best = genetic_algorithm(population)
        plot_population(best)
    except KeyboardInterrupt:
        plot_population(population[0])



if __name__ == '__main__':
    main()
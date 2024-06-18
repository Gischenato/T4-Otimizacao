import random
from KDTree import KDTree, distance, get_lowest_path_with_kdtree_greedy
import time


CIDADES = []
KD_Tree = KDTree()

START = time.time()

DO_GREEDY = True

with open('cidades.txt') as f:
    next(f)
    for line in f:
        x, y, label = line.strip().split(' ')
        CIDADES.append((float(x), float(y), label))

    # CIDADES = random.sample(CIDADES, 35)

    KD_Tree.insert_list(CIDADES)
    print(KD_Tree)
    


def branch_and_bound_dfs(cities):
    global START
    
    if DO_GREEDY:
        best_path, best_cost = get_lowest_path_with_kdtree_greedy(cities, KD_Tree, random.randint(0, len(cities) - 1))
        for i in range(20):
            current_path, current_cost = get_lowest_path_with_kdtree_greedy(cities, KD_Tree, random.randint(0, len(cities) - 1))
            if current_cost < best_cost:
                best_path, best_cost = current_path, current_cost
            
        yield best_path, best_cost
        yield best_path, best_cost
        print('--- YIELD ---')
        print(best_cost)
    else:
        best_path, best_cost = [], float('inf')
    for start_city in cities:
        all_cities = set(cities)
        all_cities.remove(start_city)
        total_cost = 0
        
        stack = [(start_city, [start_city], total_cost, all_cities.copy())]
        
        while stack:
            if time.time() - START > 2:
                START = time.time()
                yield None
            current_city, path, total_cost, remaining_cities = stack.pop()
            
            if not remaining_cities:
                total_cost += distance(current_city, start_city)
                if total_cost < best_cost:
                    print(best_cost)
                    best_path = path
                    best_cost = total_cost
                    print('--- YIELD ---')
                    print(best_cost)
                    yield best_path, best_cost
                continue
            
            for city in remaining_cities:
                new_path = path + [city]
                new_cost = total_cost + distance(current_city, city)
                new_remaining_cities = remaining_cities.copy()
                new_remaining_cities.remove(city)
                if new_cost < best_cost:
                    stack.append((city, new_path, new_cost, new_remaining_cities))
                else:
                    continue

    yield best_path, best_cost

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection

def plot_population(population):
    # print(population)
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
    plt.title('Gráfico de Pontos com Conexões')
    plt.grid(False)

    plt.draw()


import sys
def main():
    # fig = plt.figure(figsize=(10, 8))
    # fig.canvas.manager.window.wm_geometry(f"-0+0")

    def update(frame):
        if frame is None:
            # print('Timeout')
            return
        plot_population(frame[0])
    
    try:
        # ani = animation.FuncAnimation(fig, update, frames=branch_and_bound_dfs(CIDADES), repeat=False, interval=200)
        # plt.show()
        for x in branch_and_bound_dfs(CIDADES):
            pass
    except KeyboardInterrupt:
        pass
        # ani.event_source.stop()
        # plt.close(fig)
        # sys.exit(0)    


    # while True:
        # print(branch_and_bound_dfs(CIDADES))
    
main()
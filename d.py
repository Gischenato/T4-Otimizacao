from KDTree import KDTree, distance as get_distance, get_lowest_path_with_kdtree_greedy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random


CIDADES = []
KD_Tree = KDTree()

with open('data.txt') as f:
    next(f)
    for line in f:
        x, y, label = line.strip().split(' ')
        CIDADES.append((float(x), float(y), label))

    CIDADES = random.sample(CIDADES, 26)

    KD_Tree.insert_list(CIDADES)
    print(KD_Tree)
    KD_Tree.balance_tree()
    print('---------------')
    print()
    print(KD_Tree)

# path2 = get_lowest_path_greedy(CIDADES)


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

def main():
    for i in range(200):
        path, distance = get_lowest_path_with_kdtree_greedy(CIDADES, KD_Tree, start=random.randint(0, len(CIDADES) - 1))
        print(f'{i}: {distance}')
    # plot_population(path)
    # plt.show()


main()

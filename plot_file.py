import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection

def plot_population(population, gen=0, best_cost=0):
    x_coords = [point[0] for point in population]
    y_coords = [point[1] for point in population]

    plt.clf()  # Clear the current figure
    plt.scatter(x_coords, y_coords, color='blue', s=5)
    print(population)
    # Create line segments for faster plotting, excluding labels
    segments = [((x_coords[i], y_coords[i]), (x_coords[i + 1], y_coords[i + 1])) for i in range(len(population) - 1)]
    segments.append(((x_coords[-1], y_coords[-1]), (x_coords[0], y_coords[0])))  # Close the loop

    line_segments = LineCollection(segments, color='red', linewidths=0.7, linestyle='-')
    plt.gca().add_collection(line_segments)

    plt.gca().invert_yaxis()
    plt.xlabel('X')
    plt.ylabel('Y')
    # plt.title(f'\nTraveling Salesman Problem\nGenetic Algorithm\nGen: {gen}\nBest Cost: {best_cost:.2f}\nTime: {time.time() - START:.0f} seconds')
    plt.grid(False)

    plt.draw()
    plt.show()
    
    
path = []
for line in open('40.txt'):
    x, y, label = line.strip().split(' ')
    path.append((float(x), float(y), label))
    
plot_population(path)
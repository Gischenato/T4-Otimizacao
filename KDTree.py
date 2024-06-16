def distance(p1, p2):
    if p2 is None:
        return float('inf')
    # print('distance -> ',p1, p2)
    x1, y1, _ = p1
    x2, y2, _ = p2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

class KDTree():
    def __init__(self, point=None,  depth=0) -> None:
        self.point = point 
        self.left = None
        self.right = None
        # axis = 0 -> x, axis = 1 -> y
        self.axis = depth % 2
        

    def __str__(self, level=0):
        indent = " " * (4 * level)
        result = ""
        if self.point is not None:
            result += f"{indent}({self.point[0]}, {self.point[1]}, {self.point[2]})\n"
            if self.left is not None:
                result += self.left.__str__(level + 1)
            if self.right is not None:
                result += self.right.__str__(level + 1)
        else:
            result += f"{indent}None\n"
        return result

    
    def _nearest_exclude(self, root, point, depth, best, exclude_labels):
        if root is None:
            return best
        
        current_best = best

        if root.point[2] not in exclude_labels:  # Verifica se o rótulo não está excluído
            # print('root -> ', root.point)
            if best is None or distance(point, root.point) < distance(point, best):
                current_best = root.point
        
        axis = depth % 2
        next_branch = None
        opposite_branch = None

        if point[axis] < root.point[axis]:
            next_branch = root.left
            opposite_branch = root.right
        else:
            next_branch = root.right
            opposite_branch = root.left

        current_best = self._nearest_exclude(next_branch, point, depth + 1, current_best, exclude_labels)
        
        # print('current_best -> ', current_best)
        if abs(point[axis] - root.point[axis]) < distance(point, current_best):
            current_best = self._nearest_exclude(opposite_branch, point, depth + 1, current_best, exclude_labels)

        return current_best

    def nearest_neighbor(self, point, exclude_labels=None):
        if exclude_labels is None:
            exclude_labels = set()
        return self._nearest_exclude(self, point, 0, None, exclude_labels)    


    def insert(self, point: tuple):
        if self.point is None:
            self.point = point
            return
        
        if point[self.axis] < self.point[self.axis]:
            if self.left is None:
                self.left = KDTree(point, self.axis + 1)
            else:
                self.left.insert(point)
        else:
            if self.right is None:
                self.right = KDTree(point, self.axis + 1)
            else:
                self.right.insert(point)

    def insert_list(self, points_list):
        if self.point is None:
            self.point = points_list[0]
        
        for point in points_list[1:]:
            self.insert(point)


def get_lowest_path_with_kdtree_greedy(cities: list, tree: KDTree, start=0):
    start_point = cities[start]
    current_point = start_point
    path = [current_point]
    visited_labels = {current_point[2]}
    
    total_distance = 0

    while len(visited_labels) < len(cities):
        next_point = tree.nearest_neighbor(current_point, visited_labels)
        if next_point is None:
            break
        path.append(next_point)
        visited_labels.add(next_point[2])
        total_distance += distance(current_point, next_point)
        current_point = next_point
    
    total_distance += distance(current_point, start_point)

    return path, total_distance

# def get_lowest_path_greedy(cities):
#     # start = random.randint(0, len(cities) - 1)
#     start = 0
#     cities = cities.copy()
#     path = [cities.pop(start)]
#     while cities:
#         # if len(cities) % 100 == 0: print(len(cities))
#         last_city = path[-1]
#         next_city = min(cities, key=lambda city: distance(last_city, city))
#         path.append(cities.pop(cities.index(next_city)))
#     return path

# def main():
#     import random
#     import time
#     CIDADES = []
#     with open('data.txt') as data:
#         next(data)
#         for line in data:
#             x, y, name = line.strip().split()
#             CIDADES.append((float(x), float(y), name))

#     # CIDADES = random.sample(CIDADES, 50)

#     tree = KDTree()
#     for cidade in CIDADES:
#         tree.insert(cidade)

#     start = time.time()
#     for i in range(20):
#         min_path = get_lowest_path_greedy(CIDADES)
#     t1 = time.time() - start
#     start = time.time()
#     for i in range(20):
#         min_path_kdtree = get_lowest_path_with_kdtree(CIDADES, tree)
#     t2 = time.time() - start

#     exclude = set()
#     point = (3, 6, 'A')
#     while True:
#         if point is None:
#             break
#         exclude.add(point[2])
#         print(point)
#         point = tree.nearest_neighbor(point, exclude_labels=exclude)
#     # print(tree.nearest_neighbor((2, 7, 'F'), exclude_labels={'A', 'F'}))

#     print('------------------------')
#     # print(min_path)
#     # print(min_path_kdtree)
#     # check if the paths are the same
#     for p1, p2 in zip(min_path, min_path_kdtree):
#         if p1[2] != p2[2]:
#             print('Different paths')
#             break
#     print('Same paths')
#     print('Greedy time: ', t1)
#     print('KDTree time: ', t2)
#     # print(tree)


# if __name__ == "__main__":
#     main()
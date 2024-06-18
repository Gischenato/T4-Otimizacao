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

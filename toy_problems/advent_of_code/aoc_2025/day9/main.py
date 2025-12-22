
from tqdm import tqdm
import numpy as np


def sorted_indices_desc(dist):
    """
    Returns a list of [i, j] indices sorted by descending dist[i, j].
    """
    flat_idx = np.argsort(dist, axis=None)[::-1]
    rows, cols = np.unravel_index(flat_idx, dist.shape)
    return np.column_stack((rows, cols))


def main():
    print("This is a placeholder for Day 9 solution.")
    #load data from toy_problems/advent_of_code/aoc_2025/day9/data/input9.txt such that every line is an element in a list of strings
    #with open("toy_problems/advent_of_code/aoc_2025/day9/data/toy.txt", 'r') as file:
    with open("toy_problems/advent_of_code/aoc_2025/day9/data/input9.txt", 'r') as file:
        data = file.read().strip().splitlines()
    points = []
    for line in data:
        #print(line)
        points.append([int(x) for x in line.split(",")]) 
    #print(f"Points: {points}")
    print(f"Total number of lines: {len(points)}")
    #print maximum numerical value in points
    min_x = min([point[0] for point in points])
    min_y = min([point[1] for point in points])
    normalized_points = []
    for point in points:
        normalized_points.append([point[0] - min_x, point[1] - min_y])
    points = normalized_points
    max_x = max([point[0] for point in points])
    max_y = max([point[1] for point in points])
    print(f"Min x: {min_x}, Min y: {min_y}")
    print(f"Max x: {max_x}, Max y: {max_y}")
    print(f"creating grid of size {max_x+1} x {max_y+1}")
    # create 2D array of size (max_x+1) x (max_y+1) initialized to False using numpy for memory efficiency

   ## y = [False] * (max_y + 1)
   ## x = [y.copy() for _ in tqdm(range(max_x + 1))]
   

    print("Calculating distance matrix:")
    distance_matrix = [[0] * len(points) for _ in range(len(points))]
    for i in range(len(points)):
        for j in range(len(points)):
            #upper triangle only
            if j <= i:
                continue
            
            distance_matrix[i][j] = area_square(points[i], points[j])   


    x = np.zeros((max_x + 1, max_y + 1), dtype=bool)
    x[points[0][0]][points[0][1]] = True
    print("Marking paths:")
    for i in range(1,len(points)):
        if i == len(points) - 1:
            mark_path(x, points[i], points[0])
        mark_path(x, points[i-1], points[i])
        #print_grid(x)   

    # for every column, find first and last True value in x
    # print("Filling in gaps:")
    # #for cycle use parallel processing
    # #columnwise
    # for j in tqdm(range(len(x[0]))):
    #     states = np.where(x[:, j])[0]
    #     boundaries = get_boundaries_from_list(states)
    #     # print(f"Column {j}  boundaries: {boundaries}")
    #     for boundary in boundaries:
    #         x[boundary[0]:boundary[1]+1, j] = True
    #     #print_grid(x)
    
    filled_columns = np.zeros((1, len(x[0])), dtype=bool)
    
    for i,j in tqdm(sorted_indices_desc(np.array(distance_matrix))):
        for k in tqdm(range(min(points[i][1], points[j][1]), max(points[i][1], points[j][1]) + 1)):
            if not filled_columns[0][k]:
                fill_column_gaps(x, k)
                filled_columns[0][k] = True
             
        if validate_square(x, points[i], points[j]):
           print(f"Largest area square is {distance_matrix[i][j]} between points {points[i]} and {points[j]}")
           return
        
def fill_column_gaps(x, j):
    states = np.where(x[:, j])[0]
    boundaries = get_boundaries_from_list(states)
    # print(f"Column {j}  boundaries: {boundaries}")
    for boundary in boundaries:
        x[boundary[0]:boundary[1]+1, j] = True

    # # find largest distance
    # max_distance = -1
    # point1 = -1
    # point2 = -1
    # for i in range(len(points)):
    #     for j in range(len(points)):
    #         if i != j and distance_matrix[i][j] > max_distance:
    #             max_distance = distance_matrix[i][j]
    #             point1 = i
    #             point2 = j
    # print(f"Largest area square is {max_distance} between points {points[point1]} and {points[point2]}")
def get_boundaries_from_list(states):
    boundaries = []
    for i in range(0, len(states)-1):
        if states[i+1] - states[i] > 1: #there is a gap between states
            boundaries.append((states[i], states[i+1]))
            boundaries.extend(get_boundaries_from_list(states[i+2:]))
            break
    return boundaries
def validate_square(x, point1, point2):
    # check all boundary points between point1 and point2 are True
    for j in range(min(point1[1], point2[1]), max(point1[1], point2[1]) + 1):
        if not validate_point(x, (point1[0], j)):
            return False
    for i in range(min(point1[0], point2[0]), max(point1[0], point2[0]) + 1):
        if not validate_point(x, (i, point1[1])):
            return False
        # else:
        #     x[i][point1[1]] = True


        # else:
        #     x[point1[0]][j] = True
    #fill_boundaries(x, point1, point2)
    return True
def validate_point(x, point):
    return x[point[0]][point[1]]

# def validate_point(x, point):
#     # check if there is a True value in the row and column of point on both sides
#     if x[point[0]][point[1]]:
#         return True
#     if point[0] == 0 or point[1] == 0 or point[0] == len(x)-1 or point[1] == len(x[0])-1:
#         return False
#     row = point[0]
#     col = point[1]
#     has_true_in_row_after = False
#     has_true_in_col_after = False
#     has_true_in_row_before = False
#     has_true_in_col_before = False
#     sum_row_after = sum(x[row][col+1:])
#     sum_row_before = sum(x[row][:col])
#     sum_col_after = sum(x[row+1:,col])
#     sum_col_before = sum(x[:row][col])  
#     has_true_in_row_after = sum_row_after%2 != 0
#     has_true_in_row_before = sum_row_before%2 != 0
#     has_true_in_col_after = sum_col_after%2 != 0
#     has_true_in_col_before = sum_col_before%2 != 0
#     # for j in range(col,len(x[0])):
#     #     if x[row][j]:
#     #         has_true_in_row_after = True
#     #         break
#     # for j in range(col,-1,-1):
#     #     if x[row][j]:
#     #         has_true_in_row_before = True
#     #         break
#     # for i in range(row,len(x)):
#     #     if x[i][col]:
#     #         has_true_in_col_after = True
#     #         break
#     # for i in range(row,-1,-1):
#     #     if x[i][col]:
#     #         has_true_in_col_before = True
#     #         break
#     return has_true_in_row_after and has_true_in_row_before and has_true_in_col_after and has_true_in_col_before



def fill_boundaries(x, point1, point2):
    for i in range(min(point1[0], point2[0]), max(point1[0], point2[0]) + 1):
        x[i][point1[1]] = True
        x[i][point2[1]] = True
    for j in range(min(point1[1], point2[1]), max(point1[1], point2[1]) + 1):
        x[point1[0]][j] = True
        x[point2[0]][j] = True      


   # for i in range(min(point1[0], point2[0]), max(point1[0], point2[0]) + 1):
    #    for j in range(min(point1[1], point2[1]), max(point1[1], point2[1]) + 1):
    #        if not x[i][j]:
    #            return False
    #return True

def mark_path(x, start_point, end_point):
    if start_point[0] == end_point[0]:
        for i in range(min(start_point[1], end_point[1]), max(start_point[1], end_point[1]) + 1):
            x[start_point[0]][i] = True
    elif start_point[1] == end_point[1]:
        for i in range(min(start_point[0], end_point[0]), max(start_point[0], end_point[0]) + 1):
            x[i][start_point[1]] = True
    else:
        raise ValueError("Only horizontal or vertical lines are supported.")
def print_grid(x):
    for i in range(len(x)):
        row = ""
        for j in range(len(x[0])):
            if x[i][j]:
                row += "#"
            else:
                row += "."
        print(row)

def area_square(point1, point2):
    return (abs(point1[0] - point2[0])+1) * (abs(point1[1] - point2[1])+1)

if __name__ == "__main__":
    main()
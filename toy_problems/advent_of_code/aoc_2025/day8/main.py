from tqdm import tqdm
from collections import Counter
def main():
    print("This is a placeholder for Day 8 solution.")  

    #load data from toy_problems/advent_of_code/aoc_2025/day8/data/input8.txt such that every line is an element in a list of strings
    with open("toy_problems/advent_of_code/aoc_2025/day8/data/input8.txt", 'r') as file:
        data = file.read().strip().splitlines()
    points = []
    for line in data:
        print(line)
        points.append([int(x) for x in line.split(",")])

    print(f"Points: {points}")
    print(f"Total number of lines: {len(data)}")
    #construct distance matrix and initialize with max integer value
    distance_matrix = [[float('inf')] * len(points) for _ in range(len(points))]
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = euklidean_distance3D(points[i], points[j])
            distance_matrix[i][j] = dist
            distance_matrix[j][i] = dist


    connections = 0
    MAX_ITER = 10000
    circuit_ids = [-1] * len(points)
    next_circuit_id = 0
    # iterate and print progress using tmdq
    
    for x in tqdm(range(MAX_ITER)):
    
        #
        # find the minimum element in the distance matrix and collect i j indices
        min_distance = float('inf')
        min_i = -1  
        min_j = -1
        for i in range(len(points)):
            for j in range(len(points)):
                if i != j and distance_matrix[i][j] < min_distance:
                    min_distance = distance_matrix[i][j]
                    min_i = i
                    min_j = j
        distance_matrix[min_i][min_j] = float('inf')
        distance_matrix[min_j][min_i] = float('inf')
        if circuit_ids[min_i] == circuit_ids[min_j] and circuit_ids[min_i] != -1:
            continue  # already in the same circuit

        print(f"Min distance: {min_distance} between points {min_i} and {min_j}, Current circuit IDs: {circuit_ids[min_i]}, {circuit_ids[min_j]}")
        if circuit_ids[min_i] == -1 and circuit_ids[min_j] == -1: # new circuit
            circuit_ids[min_i] = next_circuit_id
            circuit_ids[min_j] = next_circuit_id
            next_circuit_id += 1
        elif circuit_ids[min_i] != -1 and circuit_ids[min_j] == -1: # append left or right
            circuit_ids[min_j] = circuit_ids[min_i]
        elif circuit_ids[min_i] == -1 and circuit_ids[min_j] != -1:
            circuit_ids[min_i] = circuit_ids[min_j]
        else:  # join circuits
            id_to_replace = circuit_ids[min_j]
            for idx in range(len(circuit_ids)):
                if circuit_ids[idx] == id_to_replace:
                    circuit_ids[idx] = circuit_ids[min_i]
       

        cntr = Counter(circuit_ids)
        print(f"Number of circuits: {len(cntr)} with sizes: {cntr}")
        if len(cntr) == 1:
            print("All points connected into a single circuit.")
            wall_distance_last_piece = points[min_i][0] * points[min_j][0]
            print(f"Wall distance of the last piece connected: {wall_distance_last_piece}")
            print(f"Last connected points: {points[min_i]} and {points[min_j]}")
            break


    print(f"Final circuit IDs: {circuit_ids}")
    cntr = Counter(circuit_ids)
    print(f"Number of circuits: {len(cntr)} with sizes: {cntr}")
    
    unconnected = cntr[-1]
    print(f"Number of unconnected points: {unconnected}")
    cntr.pop(-1,None)
    print(f"Connected circuits sizes: {cntr}")

    #get 3 largest circuits
    largest_circuits = cntr.most_common(3)
    print(f"3 largest circuits: {largest_circuits}")
    total_size = 1
    for circuit in largest_circuits:
        total_size *= circuit[1]
    print(f"Product of sizes of 3 largest circuits: {total_size}")

def euklidean_distance3D(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + 
            (point1[1] - point2[1]) ** 2 + 
            (point1[2] - point2[2]) ** 2) ** 0.5        



if __name__ == "__main__":
    #add tests for euklidean_distance3D
    assert euklidean_distance3D((0,0,0), (1,1,1)) == (3 ** 0.5)
    assert euklidean_distance3D((1,2,3), (4,5,6)) == (27 ** 0.5)


    main()

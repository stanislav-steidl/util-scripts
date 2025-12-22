from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from tqdm import tqdm
import random
import math
import numpy as np
from pathlib import Path
from typing import Optional
import os
from ortools.linear_solver import pywraplp

def main():
    print("This is a placeholder for Day 10 solution.")
    with open("toy_problems/advent_of_code/day10/data/input10.txt", 'r') as file:
        data = file.read().strip().splitlines()
    print(f"Total number of lines: {len(data)}")
    #for line in data:
        #print(line)

    settings = []
    for line in data:
        target = line.split()[0]
        button_part = line.split()[1:-1]
        button_part = [button_action[1:-1] for button_action in button_part]
        button_part = [button_action.split(',') for button_action in button_part]
        for single_button in button_part:
            for i in range(len(single_button)):
                single_button[i] = int(single_button[i])
        button_part = tuple([tuple(int(x) for x in button) for button in button_part])
        joltage_part = line.split()[-1]
        joltage_as_tuple = tuple(int(x) for x in joltage_part[1:-1].split(','))
        one_hot_button = tuple([0]*len(joltage_as_tuple))
        oh_buttons = []
        for button in button_part:
            oh_button = list(one_hot_button)
            for idx in button:
                oh_button[idx] = 1
            oh_buttons.append(tuple(oh_button))
        settings.append((target[1:-1], tuple(oh_buttons), joltage_as_tuple)) 

    #print(f"Targets: {settings}")

        est_total = 0
    for setting in settings:
        target, button_part, joltage_part = setting
        # initi
        target_setting = joltage_part
        # print(f"Processing target: {target_setting} with buttons: {button_part}")
        avg_button_contribution =sum([len(button) for button in button_part]) / len(button_part)
        target_setting_sum = sum(target_setting)
        estimated_min_steps = math.ceil(target_setting_sum / avg_button_contribution)
        est_total += estimated_min_steps
    print(f"Estimated total sum of depths: {est_total}")

    total = 0
    for i, setting in enumerate(settings):
        _ , buttons, joltage = setting
        solution = solveILP(buttons,joltage)
        presses = int(sum(solution))
        total += presses
        print(f"ID {i}: solution: {solution} total presses: {presses} ")
    print(total)

def solveLP(buttons, joltage):
    from scipy.optimize import linprog
    import numpy as np

    A = np.array(buttons).T   
    b = np.array(joltage)
    assert A.shape[0] == b.shape[0]
    n = A.shape[1]
    # print(A)
    # print(b)
    res = linprog(
        c=np.ones(n),
        A_eq=A,
        b_eq=b,
        bounds=[(0, None)] * n,
        method="highs"
    )

    x = res.x
    return x


def solveILP(buttons, joltage):
    A = np.array(buttons).T   # shape (9, 7)
    b = np.array(joltage)

    m, n = A.shape

    solver = pywraplp.Solver.CreateSolver("SCIP")

    # Integer variables x >= 0
    x = [solver.IntVar(0, solver.infinity(), f"x{i}") for i in range(n)]

    # Constraints: A x = b
    for i in range(m):
        solver.Add(
            sum(A[i, j] * x[j] for j in range(n)) == b[i]
        )

    # Objective: minimize sum(x)
    solver.Minimize(sum(x))

    status = solver.Solve()
    result = []
    if status == pywraplp.Solver.OPTIMAL:
        print("Optimal solution:")
        for i, xi in enumerate(x):
            print(f"x{i} = {int(xi.solution_value())}")
            result.append(int(xi.solution_value()))
        print("Min sum =", solver.Objective().Value())
    else:
        print("No solution")
    return result

#     TOTAL_UNITS = 18000
#     total_sum = 0
#     with ProcessPoolExecutor(max_workers=workers) as executor:
#         indexed = list(enumerate(settings))
    
#         # shuffle the pairs
#         random.shuffle(indexed)
        
#         # unpack into values and original indices
#         original_indices, shuffled_values = zip(*indexed)
#         futures = [executor.submit(process_machine, s, i) for i, s in zip(original_indices,shuffled_values)]
#         # for f in tqdm(as_completed(futures), total=len(futures)):
#         #     total_sum += f.result()
#         # for result in tqdm(executor.map(process_machine, settings), total=len(settings)):
#         #     total_sum += result
#         with tqdm(total=TOTAL_UNITS, unit="unit") as pbar:
#             for f in as_completed(futures):
#                 result = f.result()
#                 total_sum += result
#                 pbar.update(result)

#     print(f"Total sum of depths: {total_sum}")


# def save_int(filename: str | Path, value: int) -> None:
#     """Save an integer to a file."""
#     path = Path(filename)
#     path.write_text(str(value), encoding="utf-8")


# def load_int_if_exists(filename: str | Path) -> Optional[int]:
#     """
#     Return the stored integer if the file exists, otherwise None.
#     Raises ValueError if file content is not a valid int.
#     """
#     path = Path(filename)
#     if not path.exists():
#         return None
#     return int(path.read_text(encoding="utf-8").strip())

# def construct_filepath(a: str) -> Path:
#     """
#     Construct a cache file path for a given string `a`.
#     Example: 'a' -> 'toy_problems/advent_of_code/day10/cache/a.txt'
#     """
#     base = Path("toy_problems") / "advent_of_code" / "day10" / "cache"
#     base.mkdir(parents=True, exist_ok=True)  # ensure directory exists
#     return base / f"{a}.txt"


# def process_machine(setting, id)->int:
#     print(f"ID {id}: in progress")
#     cached = load_int_if_exists(construct_filepath(id))
#     if cached is None:
#         target, button_part, joltage_part = setting
#         # initi
#         target_setting = joltage_part
#         # print(f"Processing target: {target_setting} with buttons: {button_part}")
#         # avg_button_contribution =sum([len(button) for button in button_part]) / len(button_part)
#         # target_setting_sum = sum(target_setting)
#         # estimated_min_steps = math.ceil(target_setting_sum / avg_button_contribution)
#         # print(f"Estimated min steps: {estimated_min_steps} (Avg button contribution: {avg_button_contribution}, Target sum: {target_setting_sum})")
#         root = TreeNodeJoltage(parent=None, children=button_part, depth=0, state=tuple([0]*len(target_setting)), action=None, target=target_setting)
#         bfs = BreadthFirstSearch(root, tuple(target_setting))
#         result_node = bfs.search()
#         assert result_node is not None, f"No solution found for {target_setting}"
#         action_sequence = []
#         current_node = result_node
#         while current_node.parent is not None:
#             action_sequence.append(current_node.action)
#             current_node = current_node.parent
#         action_sequence = action_sequence[::-1]
#         #print(f"Action sequence for {target}: {action_sequence}")
#         save_int(construct_filepath(id),result_node.depth)
#         result = result_node.depth
#         print(f"ID {id}: Found solution for {target_setting}: {result}")
#     else:
#         result = cached
#         print(f"ID {id}: Found Cached solution: {result}")
#     # print(f"{id}: Found solution for {target_setting}: {result_node.depth}, Estimated min steps: {estimated_min_steps} ")
#     return result

# class PriorityQueue:
#     def __init__(self) -> None:
#         self.elements: list[TreeNodeJoltage] = []
        
#     def is_empty(self) -> bool:
#         return not self.elements
    
#     def put(self, item: TreeNodeJoltage) -> None:
#         self.elements.append(item)

#     def get(self) -> TreeNodeJoltage:
#         return self.elements.pop(0)
    
#     def sort(self) -> None:
#         self.elements.sort()
#     def __len__(self) -> int:
#         return len(self.elements)


# class BreadthFirstSearch:
#     def __init__(self, root: TreeNode, target: tuple[int, ...]) -> None:
#         self.root = root
#         self.target = target
#         self.queue = PriorityQueue()
#         self.queue.put(root)
#         self.visited = set()
#         self.current_depth = 0
#         self.current_queue_size = 1
#         self.search_steps = 0
#         self.reporting_interval = 100000
#     def search(self) -> TreeNode | None:
#         while self.queue:
#             self.queue.sort()
#             current_node = self.queue.get()
#             if current_node.is_goal(self.target):
#                 return current_node
            
#             # if self.search_steps % self.reporting_interval == 0:
#             #      print(f"Search steps: {self.search_steps}, Queue size: {len(self.queue)}, Visited size: {len(self.visited)}")
#             # self.search_steps += 1
#             # if current_node.depth > self.current_depth:
#             #      self.queue.sort()
#             #      self.current_depth = current_node.depth
#                 # print(f"Exploring depth: {self.current_depth}, Queue size: {len(self.queue)}, Visited size: {len(self.visited)}")
#             next_nodes = current_node.next_generation()
#             #random.shuffle(next_nodes)
#             for next_node in next_nodes:
#                 if next_node.state not in self.visited:
#                     self.visited.add(next_node.state)
#                     if next_node.is_valid(self.target):
#                         if next_node.is_goal(self.target):
#                             return next_node
#                         self.queue.put(next_node)
#                     #else:
#                         #print(f"Invalid node pruned: {next_node.state} for target {self.target}")
#         return None

# # class DepthFirstSearch:
# #     def __init__(self, root: TreeNode, target: tuple[int, ...]) -> None:
# #         self.root = root
# #         self.target = target
# #         self.stack = [root]
# #         self.visited = set()
# #     def search(self) -> TreeNode | None:
# #         while self.stack:
# #             current_node = self.stack.pop()
# #             if current_node.is_goal(self.target):
# #                 return current_node
# #             next_nodes = current_node.next_generation()
# #             random.shuffle(next_nodes)
# #             for next_node in next_nodes:
# #                 if next_node.state not in self.visited:
# #                     if next_node.is_valid(self.target):
# #                         if next_node.is_goal(self.target):
# #                             return next_node
# #                         self.visited.add(next_node.state)
# #                         self.stack.append(next_node)
# #         return None


    

if __name__ == "__main__":
    main()
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
workers = max(1, os.cpu_count())
workers = 1
print(f"Using {workers} workers for parallel processing.")


class TreeNode:
    parent: TreeNode | None = None,
    children: tuple[tuple[int, ...], ...] = None,
    depth: int = 0,
    state: tuple[int, ...] = None,
    action: tuple[int, ...] = None

    def __init__(self, parent: TreeNode | None, children: tuple[tuple[int, ...], ...], depth: int, state: tuple[int, ...], action: tuple[int, ...]) -> None:
        self.parent = parent
        self.children = children
        self.depth = depth
        self.state = state
        self.action = action

    def is_goal(self, target) -> bool:
        return self.state == target

    def apply_action(self, action: tuple[int, ...]) -> tuple[int, ...]:
        new_state = list(self.state)
        for i in action:
            new_state[i] = (new_state[i] + 1) % 2
        return tuple(new_state)

    def next_generation(self) -> list['TreeNode']:
        next_nodes = []
        for child_action in self.children:
            new_node = TreeNode(parent=self,
                                 children=self.children,
                                 depth=self.depth+1,
                                 state=self.apply_action(child_action),
                                 action=child_action)
            next_nodes.append(new_node)
        return next_nodes
    
    def is_valid(self, target) -> bool:
        return True
    


class TreeNodeJoltage(TreeNode):

    def __init__(self, parent: TreeNode | None, children: tuple[tuple[int, ...], ...], depth: int, state: tuple[int, ...], action: tuple[int, ...], target) -> None:
        super().__init__(parent, children, depth, state, action)
        self.target = target

    def apply_action(self, action: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(np.add(self.state, action))

    

    def is_valid(self, target) -> bool:
        for s, t in zip(self.state, target):
            if s > t:
                return False
        return True
    
    def next_generation(self) -> list[TreeNodeJoltage]:
        next_nodes = []
        for child_action in self.children:
            depth_increase = next(x for x in child_action if x != 0)
            new_node = TreeNodeJoltage(parent=self,
                                 children=self.children,
                                 depth=self.depth+depth_increase,
                                 state=self.apply_action(child_action),
                                 action=child_action,
                                 target=self.target
                                 )
            next_nodes.append(new_node)
        return next_nodes
    
    def self_smaller_than(self, other: TreeNodeJoltage) -> bool:
        # higher value is lower depth and secondary higher sum of state is better
        # if self.depth != other.depth:
        #     return self.depth < other.depth
        
        return sum(self.state) > sum(other.state)

    def compare_to(self, other: TreeNodeJoltage) -> int:
        # higher value is lower depth and secondary higher sum of state is better
        if self.depth != other.depth:
            return self.depth - other.depth
        return sum(other.state) - sum(self.state)

    def __lt__(self, other):
        if not isinstance(other, TreeNodeJoltage):
            return NotImplemented
        return self.self_smaller_than(other)

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
            augmented = list(one_hot_button)
            augmented2 = list(one_hot_button)
            augmented3 = list(one_hot_button)
            augmented4 = list(one_hot_button)
            augmented5 = list(one_hot_button)
            for idx in button:
                oh_button[idx] = 1
                augmented[idx] = 10
                augmented2[idx] = 20
                augmented3[idx] = 50
                augmented4[idx] = 2
                augmented5[idx] = 5
            oh_buttons.append(tuple(oh_button))
            oh_buttons.append(tuple(augmented))
            oh_buttons.append(tuple(augmented2))
            oh_buttons.append(tuple(augmented3))
            oh_buttons.append(tuple(augmented4))
            oh_buttons.append(tuple(augmented5))
        random.shuffle(oh_buttons)
        settings.append((target[1:-1], tuple(oh_buttons), joltage_as_tuple)) 

    #print(f"Targets: {settings}")

    # est_total = 0
    # for setting in settings:
    #     target, button_part, joltage_part = setting
    #     # initi
    #     target_setting = joltage_part
    #     # print(f"Processing target: {target_setting} with buttons: {button_part}")
    #     avg_button_contribution =sum([len(button) for button in button_part]) / len(button_part)
    #     target_setting_sum = sum(target_setting)
    #     estimated_min_steps = math.ceil(target_setting_sum / avg_button_contribution)
    #     est_total += estimated_min_steps
    # print(f"Estimated total sum of depths: {est_total}")


    TOTAL_UNITS = 18000
    total_sum = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        indexed = list(enumerate(settings))
    
        # shuffle the pairs
        random.shuffle(indexed)
        
        # unpack into values and original indices
        original_indices, shuffled_values = zip(*indexed)
        futures = [executor.submit(process_machine, s, i) for i, s in zip(original_indices,shuffled_values)]
        # for f in tqdm(as_completed(futures), total=len(futures)):
        #     total_sum += f.result()
        # for result in tqdm(executor.map(process_machine, settings), total=len(settings)):
        #     total_sum += result
        with tqdm(total=TOTAL_UNITS, unit="unit") as pbar:
            for f in as_completed(futures):
                result = f.result()
                total_sum += result
                pbar.update(result)

    print(f"Total sum of depths: {total_sum}")


def save_int(filename: str | Path, value: int) -> None:
    """Save an integer to a file."""
    path = Path(filename)
    path.write_text(str(value), encoding="utf-8")


def load_int_if_exists(filename: str | Path) -> Optional[int]:
    """
    Return the stored integer if the file exists, otherwise None.
    Raises ValueError if file content is not a valid int.
    """
    path = Path(filename)
    if not path.exists():
        return None
    return int(path.read_text(encoding="utf-8").strip())

def construct_filepath(a: str) -> Path:
    """
    Construct a cache file path for a given string `a`.
    Example: 'a' -> 'toy_problems/advent_of_code/day10/cache/a.txt'
    """
    base = Path("toy_problems") / "advent_of_code" / "day10" / "cache"
    base.mkdir(parents=True, exist_ok=True)  # ensure directory exists
    return base / f"{a}.txt"


def process_machine(setting, id)->int:
    print(f"ID {id}: in progress")
    cached = load_int_if_exists(construct_filepath(id))
    if cached is None:
        target, button_part, joltage_part = setting
        # initi
        target_setting = joltage_part
        # print(f"Processing target: {target_setting} with buttons: {button_part}")
        # avg_button_contribution =sum([len(button) for button in button_part]) / len(button_part)
        # target_setting_sum = sum(target_setting)
        # estimated_min_steps = math.ceil(target_setting_sum / avg_button_contribution)
        # print(f"Estimated min steps: {estimated_min_steps} (Avg button contribution: {avg_button_contribution}, Target sum: {target_setting_sum})")
        root = TreeNodeJoltage(parent=None, children=button_part, depth=0, state=tuple([0]*len(target_setting)), action=None, target=target_setting)
        bfs = BreadthFirstSearch(root, tuple(target_setting))
        result_node = bfs.search()
        assert result_node is not None, f"No solution found for {target_setting}"
        action_sequence = []
        current_node = result_node
        while current_node.parent is not None:
            action_sequence.append(current_node.action)
            current_node = current_node.parent
        action_sequence = action_sequence[::-1]
        #print(f"Action sequence for {target}: {action_sequence}")
        save_int(construct_filepath(id),result_node.depth)
        result = result_node.depth
        print(f"ID {id}: Found solution for {target_setting}: {result}")
    else:
        result = cached
        print(f"ID {id}: Found Cached solution: {result}")
    # print(f"{id}: Found solution for {target_setting}: {result_node.depth}, Estimated min steps: {estimated_min_steps} ")
    return result

class PriorityQueue:
    def __init__(self) -> None:
        self.elements: list[TreeNodeJoltage] = []
        
    def is_empty(self) -> bool:
        return not self.elements
    
    def put(self, item: TreeNodeJoltage) -> None:
        self.elements.append(item)

    def get(self) -> TreeNodeJoltage:
        return self.elements.pop(0)
    
    def sort(self) -> None:
        self.elements.sort()
    def __len__(self) -> int:
        return len(self.elements)


class BreadthFirstSearch:
    def __init__(self, root: TreeNode, target: tuple[int, ...]) -> None:
        self.root = root
        self.target = target
        self.queue = PriorityQueue()
        self.queue.put(root)
        self.visited = set()
        self.current_depth = 0
        self.current_queue_size = 1
        self.search_steps = 0
        self.reporting_interval = 100000
    def search(self) -> TreeNode | None:
        while self.queue:
            self.queue.sort()
            current_node = self.queue.get()
            if current_node.is_goal(self.target):
                return current_node
            
            # if self.search_steps % self.reporting_interval == 0:
            #      print(f"Search steps: {self.search_steps}, Queue size: {len(self.queue)}, Visited size: {len(self.visited)}")
            # self.search_steps += 1
            # if current_node.depth > self.current_depth:
            #      self.queue.sort()
            #      self.current_depth = current_node.depth
                # print(f"Exploring depth: {self.current_depth}, Queue size: {len(self.queue)}, Visited size: {len(self.visited)}")
            next_nodes = current_node.next_generation()
            #random.shuffle(next_nodes)
            for next_node in next_nodes:
                if next_node.state not in self.visited:
                    self.visited.add(next_node.state)
                    if next_node.is_valid(self.target):
                        if next_node.is_goal(self.target):
                            return next_node
                        self.queue.put(next_node)
                    #else:
                        #print(f"Invalid node pruned: {next_node.state} for target {self.target}")
        return None

# class DepthFirstSearch:
#     def __init__(self, root: TreeNode, target: tuple[int, ...]) -> None:
#         self.root = root
#         self.target = target
#         self.stack = [root]
#         self.visited = set()
#     def search(self) -> TreeNode | None:
#         while self.stack:
#             current_node = self.stack.pop()
#             if current_node.is_goal(self.target):
#                 return current_node
#             next_nodes = current_node.next_generation()
#             random.shuffle(next_nodes)
#             for next_node in next_nodes:
#                 if next_node.state not in self.visited:
#                     if next_node.is_valid(self.target):
#                         if next_node.is_goal(self.target):
#                             return next_node
#                         self.visited.add(next_node.state)
#                         self.stack.append(next_node)
#         return None


    

if __name__ == "__main__":
    main()
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from tqdm import tqdm
import random
import math


import os
workers = max(1, os.cpu_count())
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

    def __init__(self, parent: TreeNode | None, children: tuple[tuple[int, ...], ...], depth: int, state: tuple[int, ...], action: tuple[int, ...]) -> None:
        super().__init__(parent, children, depth, state, action)

    def apply_action(self, action: tuple[int, ...]) -> tuple[int, ...]:
        new_state = list(self.state)
        for i in action:
            new_state[i] += 1
        return tuple(new_state)
    

    def is_valid(self, target) -> bool:
        for i in range(len(self.state)):
            if self.state[i] > target[i]:
                return False
        return True
    
    def next_generation(self) -> list[TreeNodeJoltage]:
        next_nodes = []
        for child_action in self.children:
            new_node = TreeNodeJoltage(parent=self,
                                 children=self.children,
                                 depth=self.depth+1,
                                 state=self.apply_action(child_action),
                                 action=child_action)
            next_nodes.append(new_node)
        return next_nodes
    
    def self_smaller_than(self, other: TreeNodeJoltage) -> bool:
        # higher value is lower depth and secondary higher sum of state is better
        if self.depth != other.depth:
            return self.depth < other.depth
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
        jolatage_as_tuple = tuple(int(x) for x in joltage_part[1:-1].split(','))
        settings.append((target[1:-1], button_part, jolatage_as_tuple)) 
    #print(f"Targets: {settings}")

    if False:

        total_sum = 0
        for setting in tqdm(settings):
            target, button_part, joltage_part = setting
            
            # initi
            target_setting = [0]*len(target)
            for i in range(len(target)):
                if target[i] == '#':
                    target_setting[i] = 1
            print(f"Processing target: {target_setting} with buttons: {button_part} and joltage: {joltage_part}")
            root = TreeNodeJoltage(parent=None, children=button_part, depth=0, state=tuple([0]*len(target)), action=None)
            bfs = BreadthFirstSearch(root, tuple(target_setting))
            result_node = bfs.search()
            assert result_node is not None, f"No solution found for {target}"
            action_sequence = []
            current_node = result_node
            while current_node.parent is not None:
                action_sequence.append(current_node.action)
                current_node = current_node.parent
            action_sequence = action_sequence[::-1]
            print(f"Action sequence for {target}: {action_sequence}")
            print(f"Found solution for {target}: {result_node.depth}")
            total_sum += result_node.depth
        print(f"Total sum of depths: {total_sum}")



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
    TOTAL_UNITS = est_total
    total_sum = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_machine, s, i) for i, s in enumerate(settings)]
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






def process_machine(setting, id)->int:
    target, button_part, joltage_part = setting
    # initi
    target_setting = joltage_part
    # print(f"Processing target: {target_setting} with buttons: {button_part}")
    avg_button_contribution =sum([len(button) for button in button_part]) / len(button_part)
    target_setting_sum = sum(target_setting)
    estimated_min_steps = math.ceil(target_setting_sum / avg_button_contribution)
    # print(f"Estimated min steps: {estimated_min_steps} (Avg button contribution: {avg_button_contribution}, Target sum: {target_setting_sum})")
    root = TreeNodeJoltage(parent=None, children=button_part, depth=0, state=tuple([0]*len(target_setting)), action=None)
    dfs = BreadthFirstSearch(root, tuple(target_setting))
    result_node = dfs.search()
    assert result_node is not None, f"No solution found for {target_setting}"
    action_sequence = []
    current_node = result_node
    while current_node.parent is not None:
        action_sequence.append(current_node.action)
        current_node = current_node.parent
    action_sequence = action_sequence[::-1]
    #print(f"Action sequence for {target}: {action_sequence}")
    print(f"{id}: Found solution for {target_setting}: {result_node.depth}, Estimated min steps: {estimated_min_steps} ")
    return result_node.depth

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
            current_node = self.queue.get()
            if current_node.is_goal(self.target):
                return current_node
            
            # if self.search_steps % self.reporting_interval == 0:
            #      print(f"Search steps: {self.search_steps}, Queue size: {len(self.queue)}, Visited size: {len(self.visited)}")
            # self.search_steps += 1
            if current_node.depth > self.current_depth:
                 self.queue.sort()
                 self.current_depth = current_node.depth
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
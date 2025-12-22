from __future__ import annotations

from dataclasses import dataclass
from tqdm import tqdm
from collections import deque

def main():
    print("Day 11 Advent of Code 2025")

    #read the data form file, one line as one element
    with open("toy_problems/advent_of_code/aoc_2025/day11/data/input11.txt", "r") as f:
        data = f.read().splitlines()

    seed_node = None
    sink_node = None
    node_registry: dict[str, GraphNode] = {}
    for line in data:
        id = line.split(':')[0]
        edges = []
        rest = line.split(':')[1].strip()
        for item in rest.split():
            edges.append(item.strip())

        node = GraphNode(id, edges)
        node_registry[id] = node

        print(f"ID: {id}, Rest: {edges}")


    print(f"Total nodes: {len(node_registry)}")
    node_registry["out"] = GraphNode("out", [], 1)

    for node in node_registry.values():
        for i, edge_id in enumerate(node.edges_out):
            if isinstance(edge_id, str):
                if edge_id == "you":
                    continue # we assume no cycles
                node.edges_out[i] = node_registry[edge_id]
                node_registry[edge_id].edges_in.append(node)


    pruned_nodes ={}
    orig_len = len(node_registry)
    pruning = True
    while pruning:
        for node in node_registry.values():
            if node.id == "you" or len(node.edges_in) > 0:
                pruned_nodes[node.id] = node
            else: #node is not reachable and not seed: remove it from its parents
                for out_node in node.edges_out:
                    if isinstance(out_node, GraphNode):
                        out_node.edges_in.remove(node)
       
        if len(pruned_nodes) == len(node_registry):
            pruning = False
        else:
            node_registry = pruned_nodes
            pruned_nodes = {}
    pruned_len = len(node_registry)
    print(f"Pruned nodes from {orig_len} to {pruned_len}")

    for node in node_registry.values():
        print(f"Node {node.id} has edges out: {[e.id if isinstance(e, GraphNode) else e for e in node.edges_out]} and edges in: {[e.id for e in node.edges_in]}")

    sink_node = node_registry["out"]
    node_queue = [sink_node]
    while len(node_queue) > 0:
        current_node = node_queue.pop(0)
        for parent_node in current_node.edges_in:
            
            parent_node.value += 1 #current_node.value
            #print(f"Updated node {parent_node.id} value to {parent_node.value} from child {current_node.id} with value {current_node.value}")
            node_queue.append(parent_node)
    print(f"Value at seed node: {node_registry['you'].value}")

def main2():
    print("Day 11 Advent of Code 2025 - Part 2")
    #read the data form file, one line as one element
    with open("toy_problems/advent_of_code/aoc_2025/day11/data/input11.txt", "r") as f:
        data = f.read().splitlines()
    server_id = 'svr'
    sink_node = None
    node_registry: dict[str, GraphNode] = {}
    for line in data:
        id = line.split(':')[0]
        edges = []
        rest = line.split(':')[1].strip()
        for item in rest.split():
            edges.append(item.strip())

        node = GraphNode(id, edges)
        node_registry[id] = node

        # print(f"ID: {id}, Rest: {edges}")


    print(f"Total nodes: {len(node_registry)}")
    node_registry["out"] = GraphNode("out", [], 1)

    for node in node_registry.values():
        new_edges = []
        for edge in node.edges_out:
            if isinstance(edge, str):
                new_edges.append(node_registry[edge])
            else:
                new_edges.append(edge)
        node.edges_out = new_edges
        for edge in node.edges_out:
            edge.edges_in.append(node)
        # for i, edge_id in enumerate(node.edges_out):
        #     if isinstance(edge_id, str):
        #         # if edge_id == server_id:
        #         #     continue # we assume no cycles
        #         node.edges_out[i] = node_registry[edge_id]
        #         node_registry[edge_id].edges_in.append(node)


    # pruned_nodes ={}
    # orig_len = len(node_registry)
    # pruning = True
    # while pruning:
    #     for node in node_registry.values():
    #         if node.id == server_id or len(node.edges_in) > 0:
    #             pruned_nodes[node.id] = node
    #         else: #node is not reachable and not seed: remove it from its parents
    #             for out_node in node.edges_out:
    #                 if isinstance(out_node, GraphNode):
    #                     out_node.edges_in.remove(node)
       
    #     if len(pruned_nodes) == len(node_registry):
    #         pruning = False
    #     else:
    #         node_registry = pruned_nodes
    #         pruned_nodes = {}
    # pruned_len = len(node_registry)
    # print(f"Pruned nodes from {orig_len} to {pruned_len}")
    print_graph(node_registry)
    

    paths_of_interest = [['svr','dac'],['svr','fft'],['dac','fft'],['fft','dac'],['dac','out'],['fft','out']] 
    results_collection = []
    ban_list = set(["svr","out","dac","fft"])
    for pth in tqdm(paths_of_interest):
        for node in node_registry.values():
            node.value = 0

        nogo = set(list(ban_list - set([pth[0], pth[1]])))
        source_node = pth[0]
        target_node = pth[1] 
        nodes_for_pruning = deep_copy(node_registry)
        # print_graph(nodes_for_pruning)
        pruned_node_registry = prune_nodes(nodes_for_pruning, source_node, target_node)
        # print_graph(pruned_node_registry)
        pruned_node_registry = deep_copy(pruned_node_registry)
        topo_order = topological_sort(pruned_node_registry)
        pruned_node_registry[source_node].value = 1
        for el in topo_order:
            for child in el.edges_out:
                child.value += el.value



        # sink_node = pruned_node_registry[target_node]
        # sink_node.value = 1
        # node_queue = [sink_node]
        # while len(node_queue) > 0:
        #     current_node = node_queue.pop(0)
        #     for parent_node in current_node.edges_in:
        #         if parent_node.id in nogo:
        #             continue
        #         parent_node.value += 1 #current_node.value
        #         #print(f"Updated node {parent_node.id} value to {parent_node.value} from child {current_node.id} with value {current_node.value}")
        #         if parent_node.id != source_node:
        #             node_queue.append(parent_node)
        results_collection.append((pth, pruned_node_registry[target_node].value))
        print(f"Value at seed node: {pruned_node_registry[target_node].value}")
    viable_paths = [[0,2,5],[1,3,4]]
    total_total = 0
    for path in viable_paths:
        total = 1
        for idx in path:
            total *= results_collection[idx][1]
        print(f"Path {[results_collection[idx][0] for idx in path]} has total combinations: {total}")
        total_total += total
    print(f"Total combinations to reach out: {total_total}")

def topological_sort(nodes):
    """
    Returns a list of GraphNode in topological order.
    Raises ValueError if a cycle is detected.
    """

    # --- compute indegrees ---
    indegree = {node_id: 0 for node_id in nodes}

    for node in nodes.values():
        for parent in node.edges_in:
            indegree[node.id] += 1

    # --- initialize queue with zero-indegree nodes ---
    queue = deque(
        node for node_id, node in nodes.items()
        if indegree[node_id] == 0
    )

    topo = []

    # --- Kahn's algorithm ---
    while queue:
        u = queue.popleft()
        topo.append(u)

        for v in u.edges_out:
            # normalize edge type
            v_id = v.id if isinstance(v, GraphNode) else v
            indegree[v_id] -= 1

            if indegree[v_id] == 0:
                queue.append(nodes[v_id])

    # --- cycle detection ---
    if len(topo) != len(nodes):
        raise ValueError("Graph contains a cycle")

    return topo

def print_graph(node_registry):
    for node in node_registry.values():
        print(f"Node {node.id} has edges out: {[e.id if isinstance(e, GraphNode) else e for e in node.edges_out]} and edges in: {[e.id for e in node.edges_in]}")


def deep_copy(node_registry):
    new_registry = {}
    for node in node_registry.values():
        new_node = node.copy()
        new_registry[new_node.id] = new_node
    for node in new_registry.values():
        new_node = node.deep_copy(new_registry)
        new_registry[new_node.id] = new_node
    for node in new_registry.values():
        for i, edge in enumerate(node.edges_out):
            if isinstance(edge, GraphNode):
                node.edges_out[i] = new_registry[edge.id]
            else:
                node.edges_out[i] = new_registry[edge]
        for i, edge in enumerate(node.edges_in):
            node.edges_in[i] = new_registry[edge.id]
    return new_registry

def prune_nodes(node_registry, source_node, target_node):
    pruned_nodes ={}
    previous_registry = node_registry
    prev_len = len(previous_registry)
    pruning = True
    while pruning:
        queue = [previous_registry[target_node]]

        reachable_up = set()
        reachable_up.add(target_node)
        
        while len(queue) > 0:
            current_node = queue.pop(0)
            for parent_node in current_node.edges_in:
                if parent_node.id not in reachable_up:
                    reachable_up.add(parent_node.id)
                    queue.append(parent_node)
        reachable_up.add(source_node)


        queue_down = [previous_registry[source_node]]
        reachable_down = set()
        reachable_down.add(source_node)
        
        while len(queue_down) > 0:
            current_node = queue_down.pop(0)
            for child_node in current_node.edges_out:
                if isinstance(child_node, GraphNode):
                    if child_node.id not in reachable_down:
                        reachable_down.add(child_node.id)
                        queue_down.append(child_node)
        reachable_down.add(target_node)
        pruned_ids = reachable_up.intersection(reachable_down)
        # print(f"Reachable up: {reachable_up}, Reachable down: {reachable_down}, Pruned IDs: {pruned_ids}")
        for idx in pruned_ids:
            assert idx in previous_registry
            pruned_nodes[idx] = previous_registry[idx]

        for node in pruned_nodes.values():
            new_edges_out = []
            for edge in node.edges_out:
                assert isinstance(edge, GraphNode) 
                if edge.id in pruned_ids:
                    new_edges_out.append(edge)
            node.edges_out = new_edges_out

            new_edges_in = []
            for edge in node.edges_in:
                if edge.id in pruned_ids:
                    new_edges_in.append(edge)
            node.edges_in = new_edges_in

        if len(pruned_nodes) == len(previous_registry):
            pruning = False
            previous_registry = pruned_nodes
        else:
            previous_registry = pruned_nodes
            pruned_nodes = {}
    print(f"Pruned nodes from {prev_len} to {len(previous_registry)}")
    return previous_registry
        

class GraphNode:

    id: str
    edges_out: list[GraphNode| str] 
    edges_in: list[GraphNode]
    value: int

    def __init__(self, id: str, edges_out: list[str], value: int = 0):
        self.id = id
        self.edges_out = edges_out
        self.value = value
        self.edges_in = []

    def copy(self) -> GraphNode:
        edges_out = self.edges_out.copy()
        edges_in = self.edges_in.copy()
        new_node = GraphNode(self.id, edges_out, self.value)
        new_node.edges_in = edges_in
        return new_node

    def deep_copy(self, node_list) -> GraphNode:
        edges_out = []
        edges_in = []
        for edge in self.edges_out:
            edges_out.append(node_list[edge.id])
        for edge in self.edges_in:
            edges_in.append(node_list[edge.id])
        new_node = GraphNode(self.id, edges_out, self.value)
        new_node.edges_in = edges_in
        return new_node





if __name__ == "__main__":
    #main()
    main2()
from dataclasses import dataclass
import numpy as np
from typing import List, Tuple
import random
import time
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

@dataclass
class Present:
    id: int
    detail: np.ndarray  # boolean mask

    def list_all_variants(self) -> List[np.ndarray]:
        obj = self.detail
        return [
            obj,
            np.rot90(obj, 1),
            np.rot90(obj, 2),
            np.rot90(obj, 3),
            np.fliplr(obj),
            np.flipud(obj),
            np.rot90(np.fliplr(obj)),
            np.rot90(np.flipud(obj)),
        ]

def can_place(grid: np.ndarray, shape: np.ndarray, top: int, left: int) -> bool:
    h, w = shape.shape
    gh, gw = grid.shape
    if top + h > gh or left + w > gw:
        return False
    subgrid = grid[top:top+h, left:left+w]
    # shape cells must not overlap occupied cells
    return not np.any(subgrid & shape)

def place_shape(grid: np.ndarray, shape: np.ndarray, top: int, left: int, mark: bool):
    h, w = shape.shape
    grid[top:top+h, left:left+w] |= shape if mark else (~shape & grid[top:top+h, left:left+w])

def region_fits_with_timeout(grid_shape: Tuple[int,int],
                             present_counts: List[int],
                             all_presents: List["Present"],
                             timeout_sec: float = 1.0) -> bool:
    """
    Try to fit presents into the grid with a timeout.
    Returns True if all presents fit, False if timeout or impossible.
    """
    H, W = grid_shape
    cache_file = CACHE_DIR / f"{H}_{W}_{'_'.join(map(str, present_counts))}.txt"

    if cache_file.exists():
        return cache_file.read_text().strip() == "1"
    
    grid = np.zeros(grid_shape, dtype=bool)
    start_time = time.time()

    # prepare presents list
    presents_to_place = [(p, present_counts[p.id]) for p in all_presents if present_counts[p.id] > 0]

    def backtrack(grid: np.ndarray, presents_to_place: List[Tuple["Present", int]]) -> bool:
        # check timeout
        if time.time() - start_time > timeout_sec:
            print("Timed out")
            return False

        if all(count == 0 for _, count in presents_to_place):
            return True  # all placed

        # prepare candidates with their indices
        candidates = [(idx, p, count) 
                      for idx, (p, count) in enumerate(presents_to_place) 
                      if count > 0]

        # prioritize by max remaining count
        max_count = max(c[2] for c in candidates)
        max_candidates = [c for c in candidates if c[2] == max_count]
        np.random.shuffle(max_candidates)  # random tie-break

        for idx, present, count in max_candidates:
            for variant in present.list_all_variants():
                vh, vw = variant.shape
                gh, gw = grid.shape

                for i in range(gh - vh + 1):
                    for j in range(gw - vw + 1):
                        if np.all((grid[i:i+vh, j:j+vw] & variant) == 0):
                            # place variant
                            grid[i:i+vh, j:j+vw] |= variant

                            # update remaining count
                            new_presents = presents_to_place.copy()
                            new_presents[idx] = (present, count - 1)

                            if backtrack(grid, new_presents):
                                return True
                            else:
                                if time.time() - start_time > timeout_sec:
                                    print("Timed out")
                                    return False
                            # backtrack
                            grid[i:i+vh, j:j+vw] &= ~variant

        return False
    solvable = backtrack(grid, presents_to_place)
    if solvable:
        cache_file.write_text("1")  # save only successful result

    return solvable






def solve12(presents, grid_defs):
    total_solvable = 0
    for grid in grid_defs:
        tree_id, tree_size, req_boxes = grid
        print(f"Solving grid id {tree_id}")
        solvable = region_fits_with_timeout(tuple(tree_size),list(req_boxes),presents)
        if  solvable:
            total_solvable += 1
            print(f"found solution for {grid}")
        else:
            print(f"No solution for {grid}")
        
    return total_solvable

def main():
    print("Day 12 Advent of Code 2025")
    with open("toy_problems/advent_of_code/aoc_2025/day12/data/input12.txt", "r") as f:
        data = f.read().splitlines()
    grouped_lines = [[]]
    object_iterator  = 0
    for line in data:
        if line != "":
            grouped_lines[object_iterator].append(line)
        else:
            grouped_lines.append([])
            object_iterator += 1

    for group in grouped_lines:
        print(group)
    trees = grouped_lines[-1]
    boxes = grouped_lines[:-1]
    presents = []
    for box in boxes:
        id = int(box[0].split(":")[0])
        detail_str = box[1:]
        shape = tuple([len(detail_str),len(detail_str[0])])
        detail_bool =  np.zeros((shape), dtype=bool)
        for i in range(shape[0]):
            for j in range(shape[1]):
                if detail_str[i][j] == "#":
                    detail_bool[i,j] = True
        presents.append(Present(id,detail_bool))
        print(f'ID {id}, hull {shape}, detail {detail_bool}')

    tree_id = 0
    grid_defs= []
    for tree in trees:
        tree_size = tree.split(':')[0]
        tree_size = tree_size.split('x')
        tree_size = tuple([int(x) for x in tree_size])
        req_boxes = tree.split(':')[-1]
        req_boxes = tuple([int(x) for x in req_boxes.split()])
        print(f"ID {tree_id}, tree size {tree_size}, requires {req_boxes}")
        grid_defs.append([tree_id, tree_size, req_boxes])
        tree_id +=1

    print(f"total solvable: {solve12(presents, grid_defs)}")

if __name__ == "__main__":
    main()
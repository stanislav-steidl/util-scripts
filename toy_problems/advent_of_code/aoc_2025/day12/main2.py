from tqdm import tqdm
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from ortools.sat.python import cp_model
import hashlib
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.txt"


def cache_lookup(key: str) -> bool | None:
    path = cache_path(key)
    if not path.exists():
        return None
    return path.read_text().strip() == "1"


def cache_store(key: str, solvable: bool):
    cache_path(key).write_text("1" if solvable else "0")

# ----------------------------
# Utilities
# ----------------------------

def unique_variants(masks: list[NDArray[np.bool_]]) -> list[NDArray[np.bool_]]:
    unique = []
    for m in masks:
        if not any(np.array_equal(m, u) for u in unique):
            unique.append(m)
    return unique


def bounding_box(mask: NDArray[np.bool_]):
    ys, xs = np.where(mask)
    return ys.min(), ys.max(), xs.min(), xs.max()


# ----------------------------
# Data class
# ----------------------------

@dataclass
class Present:
    id: int
    detail: NDArray[np.bool_]

    def variants(self) -> list[NDArray[np.bool_]]:
        m = self.detail
        return unique_variants([
            m,
            np.rot90(m),
            np.rot90(m, 2),
            np.rot90(m, 3),
            np.fliplr(m),
            np.flipud(m),
            np.rot90(np.fliplr(m)),
            np.rot90(np.flipud(m)),
        ])

# ----------------------------
# Solver
# ----------------------------
def masks_overlap(xi, yi, mi, xj, yj, mj):
    hi, wi = mi.shape
    hj, wj = mj.shape

    x0 = max(xi, xj)
    y0 = max(yi, yj)
    x1 = min(xi + wi, xj + wj)
    y1 = min(yi + hi, yj + hj)

    if x0 >= x1 or y0 >= y1:
        return False

    si = mi[y0 - yi : y1 - yi, x0 - xi : x1 - xi]
    sj = mj[y0 - yj : y1 - yj, x0 - xj : x1 - xj]

    return np.any(si & sj)

from collections import defaultdict
import time



def add_overlap_constraints_fast(
    model,
    placements,
    select_vars,
    log_every: float = 2.0,
):
    """
    placements: (p_idx, x, y, mask, (h, w), area)
    """

    t0 = time.time()
    last_log = t0

    # ----------------------------
    # Build spatial buckets
    # ----------------------------
    cell_map = defaultdict(list)

    for i, (_, x, y, _, (h, w), _) in enumerate(placements):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                cell_map[(yy, xx)].append(i)

        now = time.time()
        if now - last_log > log_every:
            print(f"  bucketed {i+1}/{len(placements)} placements")
            last_log = now

    # ----------------------------
    # Add exact overlap constraints
    # ----------------------------
    seen = set()
    added = 0

    for ids in cell_map.values():
        if len(ids) < 2:
            continue

        for a_i in range(len(ids)):
            for b_i in range(a_i + 1, len(ids)):
                a, b = ids[a_i], ids[b_i]
                if a > b:
                    a, b = b, a
                if (a, b) in seen:
                    continue
                seen.add((a, b))

                _, xa, ya, ma, _, _ = placements[a]
                _, xb, yb, mb, _, _ = placements[b]

                if masks_overlap(xa, ya, ma, xb, yb, mb):
                    model.Add(select_vars[a] + select_vars[b] <= 1)
                    added += 1

    print(f"  added {added} overlap constraints in {time.time() - t0:.2f}s")

def estimate_difficulty(presents, grid_size, requires):
    H, W = grid_size
    grid_area = H * W

    total_area = sum(
        p.detail.sum() * requires[i]
        for i, p in enumerate(presents)
    )

    density = total_area / grid_area

    max_copies = max(requires)
    unique_shapes = sum(
        len(p.variants()) for p in presents
    )

    score = (
        3.0 * density +
        0.5 * unique_shapes +
        0.3 * max_copies
    )

    return score

def grid_solvable_cached(presents, grid_size, requires) -> bool:
    key = instance_hash(presents, grid_size, requires)

    cached = cache_lookup(key)
    if cached is not None:
        return cached

    result = grid_solvable(presents, grid_size, requires)

    if result is None:
        # timeout → do NOT cache
        print(f"⚠️  timeout for {grid_size}, {requires}")
        return False   # or raise / log / skip depending on your needs


    cache_store(key, result)
    return result

def grid_solvable(presents: list[Present], grid_size, requires) -> bool:
    H, W = grid_size
    model = cp_model.CpModel()

    # ---- build all placement candidates
    placements = []  # (present_id, x, y, mask, bbox, area)


    for p_idx, p in tqdm(enumerate(presents)):
        variants = p.variants()
        for mask in variants:
            y0, y1, x0, x1 = bounding_box(mask)
            h = y1 - y0 + 1
            w = x1 - x0 + 1
            area = int(mask.sum())

            for y in range(H - h + 1):
                for x in range(W - w + 1):
                    area = int(mask.sum())
                    placements.append(
                        (p_idx, x - x0, y - y0, mask, (h, w), area)
                    )

    # ---- group placements by present
    placements_by_present = {}
    for i, p in enumerate(placements):
        placements_by_present.setdefault(p[0], []).append(i)

    # ---- create selection vars
    select = [
        model.NewBoolVar(f"pl_{i}") for i in range(len(placements))
    ]

    # ---- required counts
    for p_idx, req in enumerate(requires):
        model.Add(
            sum(select[i] for i in placements_by_present[p_idx]) == req
        )

    # # ---- non-overlap constraints (pairwise)
    # for i in tqdm(range(len(placements))):
    #     pi, xi, yi, mi, _, _ = placements[i]
    #     for j in range(i + 1, len(placements)):
    #         pj, xj, yj, mj, _, _ = placements[j]

    #         if masks_overlap(xi, yi, mi, xj, yj, mj):
    #             model.Add(select[i] + select[j] <= 1)
    add_overlap_constraints_fast(
        model=model,
        placements=placements,
        select_vars=select,
    )

    # ---- search ordering (dense first)
    ordering = sorted(
        range(len(select)),
        key=lambda i: placements[i][5],
        reverse=True
    )

    model.AddDecisionStrategy(
        [select[i] for i in ordering],
        cp_model.CHOOSE_FIRST,
        cp_model.SELECT_MAX_VALUE
    )

    # ---- solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return True
    if status == cp_model.INFEASIBLE:
        return False

    # UNKNOWN / timeout
    return None

# ----------------------------
# Top-level solve function
# ----------------------------
def solve12(presents, grid_defs):
    solvable = 0
    for grid in grid_defs:
        print(f"Solving grid id {grid[0]}")
        difficulty = estimate_difficulty(presents, grid[1], grid[2])
        print(f"instance difficulty ≈ {difficulty:.2f}")
        if  grid_solvable_cached(presents, grid[1], grid[2]):
            solvable += 1
            print(f"found solution for {grid}")
        else:
            print(f"No solution for {grid}")
        
    return solvable

def instance_hash(presents, grid_size, requires) -> str:
    h = hashlib.sha256()

    h.update(np.array(grid_size, dtype=np.int32).tobytes())
    h.update(np.array(requires, dtype=np.int32).tobytes())

    for p in presents:
        h.update(p.detail.astype(np.uint8).tobytes())

    return h.hexdigest()

# ----------------------------
# Main function: example usage
# ----------------------------
def main_test():
    print("Day 12 Advent of Code 2025")

    # Example setup (replace with your file parsing)
    # 6 presents with random 3x3 masks
    presents = [
        Present(0, np.array([[1,0,1],[1,1,0],[0,1,0]], bool)),
        Present(1, np.array([[1,1,0],[0,1,1],[0,0,1]], bool)),
        Present(2, np.array([[1,0,1],[0,1,0],[1,0,1]], bool)),
        Present(3, np.array([[1,1,1],[0,1,0],[1,0,1]], bool)),
        Present(4, np.array([[1,0,0],[1,1,1],[0,1,0]], bool)),
        Present(5, np.array([[0,1,0],[1,1,0],[1,0,1]], bool)),
    ]
    # Example grid: 35x50, required counts for each present
    grid_defs = [(0, (35, 50), (5, 4, 3, 3, 4, 3))]

    print(f"Total solvable grids: {solve12(presents, grid_defs)}")


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
        id = box[0].split(":")[0]
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

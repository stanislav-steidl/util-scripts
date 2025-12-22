import numpy as np
from dataclasses import dataclass
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

@dataclass
class Present:
    id: int
    detail: np.ndarray  # 3x3 boolean mask

    def list_all_variants(self):
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

# -----------------------
# Bitboard conversion
# -----------------------
def mask_to_bitrows(mask):
    """Convert boolean 2D mask to list of integers (bitboard per row)."""
    h, w = mask.shape
    rows = []
    for i in range(h):
        val = 0
        for j in range(w):
            if mask[i,j]:
                val |= 1 << j
        rows.append(val)
    return rows, w, h

def can_place_bitboard(grid_rows, mask_rows, x, y, W):
    """Check if mask can be placed at (x,y) on grid_rows."""
    for dy, row_val in enumerate(mask_rows):
        shifted = row_val << x
        if y + dy >= len(grid_rows):
            return False
        if (grid_rows[y + dy] & shifted) != 0:
            return False
        if shifted >= (1 << W):
            return False
    return True

def place_bitboard(grid_rows, mask_rows, x, y):
    for dy, row_val in enumerate(mask_rows):
        grid_rows[y + dy] ^= (row_val << x)

# -----------------------
# Solver
# -----------------------
def create_compound_blocks(presents):
    compounds = []
    n = len(presents)
    for i in range(n):
        for j in range(i+1, n):
            p1 = presents[i]
            p2 = presents[j]
            for v1 in p1.list_all_variants():
                h1, w1 = v1.shape
                for v2 in p2.list_all_variants():
                    h2, w2 = v2.shape
                    # Try all relative positions (dx, dy) where top-left of v2 relative to v1
                    for dy in range(-h2+1, h1):
                        for dx in range(-w2+1, w1):
                            # Shift v2 by dx, dy
                            canvas_h = max(h1, dy + h2 if dy >= 0 else h1 - dy)
                            canvas_w = max(w1, dx + w2 if dx >= 0 else w1 - dx)
                            if canvas_h > 45 or canvas_w > 45:  # assume max grid 45
                                continue
                            canvas = np.zeros((canvas_h, canvas_w), dtype=bool)
                            # Place v1 at (0,0)
                            canvas[0:h1, 0:w1] |= v1
                            # Compute v2 position
                            y2 = max(dy,0)
                            x2 = max(dx,0)
                            # Compute offset for negative shifts
                            y2_offset = -min(dy,0)
                            x2_offset = -min(dx,0)
                            # Check overlap
                            subcanvas = canvas[y2:y2+h2, x2:x2+w2]
                            if np.any(subcanvas & v2):
                                continue
                            # Place v2
                            canvas[y2:y2+h2, x2:x2+w2] |= v2
                            compounds.append({'ids': (p1.id,p2.id), 'mask': canvas})
    return compounds


def tetris_solver(grid_shape, presents, requires):

    H, W = grid_shape
    cache_file = CACHE_DIR / f"{H}_{W}_{'_'.join(map(str, requires))}.txt"

    if cache_file.exists():
        return cache_file.read_text().strip() == "1"

    compounds = create_compound_blocks(presents)

    if not quick_feasibility_compound(grid_shape, presents, requires, compounds):
        return False  # skip expensive DFS/backtracking


    # Area check
    total_cells = sum(np.sum(p.detail) * count for p, count in zip(presents, requires))
    if total_cells > H * W:
        return False

    # Precompute variants as bitboards
    present_info = []
    for p, count in zip(presents, requires):
        variants = []
        for v in p.list_all_variants():
            rows, w, h = mask_to_bitrows(v)
            if w <= W and h <= H:  # fits grid
                variants.append((rows, w, h))
        present_info.append({'present': p, 'count': count, 'variants': variants})

    # Flatten list of present copies
    flat_variants = []
    for info in present_info:
        for _ in range(info['count']):
            # sort variants by number of bits set (densest first)
            var_sorted = sorted(info['variants'], key=lambda x: -sum(bin(r).count("1") for r in x[0]))
            flat_variants.append(var_sorted)

    grid_rows = [0] * H  # empty grid
    seen_states = set()

    # -----------------------
    # Memoized DFS
    # -----------------------
    def dfs(idx):
        if idx >= len(flat_variants):
            return True

        state = tuple(grid_rows)
        if state in seen_states:
            return False
        seen_states.add(state)

        for rows, w_mask, h_mask in flat_variants[idx]:
            for y in range(H - h_mask + 1):
                for x in range(W - w_mask + 1):
                    if can_place_bitboard(grid_rows, rows, x, y, W):
                        place_bitboard(grid_rows, rows, x, y)
                        if dfs(idx + 1):
                            return True
                        place_bitboard(grid_rows, rows, x, y)  # undo
        return False

    solvable = dfs(0)

    if solvable:
        cache_file.write_text("1")  # save only successful result

    return solvable

def min_row_col_sums(presents, requires):
    """Compute realistic lower bounds for row/col occupation of grid."""
    row_sums = []
    col_sums = []
    for p, count in zip(presents, requires):
        max_row = 0
        max_col = 0
        for v in p.list_all_variants():
            row_max_v = max(np.sum(v, axis=1))  # max cells in any row
            col_max_v = max(np.sum(v, axis=0))  # max cells in any col
            max_row = max(max_row, row_max_v)
            max_col = max(max_col, col_max_v)
        row_sums.append(max_row * count)
        col_sums.append(max_col * count)
    return sum(row_sums), sum(col_sums)

def quick_feasibility(grid_shape, presents, requires):
    H, W = grid_shape

    # 1. Total filled cells
    total_cells = sum(np.sum(p.detail) * count for p, count in zip(presents, requires))
    if total_cells > H * W:
        return False

    # 2. Max object size
    max_w = max(max(v.shape[1] for v in p.list_all_variants()) for p in presents)
    max_h = max(max(v.shape[0] for v in p.list_all_variants()) for p in presents)
    if max_w > W or max_h > H:
        return False

    # 3. Sum of minimum widths/heights
    total_min_row, total_min_col = min_row_col_sums(presents, requires)
    if total_min_row > H or total_min_col > W:
        return False  # definitely impossible

    return True

def quick_feasibility_compound(grid_shape, presents, requires, compounds):
    """
    grid_shape: (H,W)
    presents: list of Present objects
    requires: list of counts
    compounds: list of precomputed compound blocks
    """
    H, W = grid_shape

    # 1. Total filled cells
    total_cells = sum(np.sum(p.detail) * count for p, count in zip(presents, requires))
    if total_cells > H * W:
        return False  # definitely impossible

    # 2. Largest variant fits
    max_w = max(max(v.shape[1] for v in p.list_all_variants()) for p in presents)
    max_h = max(max(v.shape[0] for v in p.list_all_variants()) for p in presents)
    if max_w > W or max_h > H:
        return False

    # 3. Compound block coverage heuristic
    # Compute total coverage if we use all compounds optimally
    # Sum filled cells of all compounds
    compound_cells = [np.sum(c['mask']) for c in compounds]
    compound_cells_sorted = sorted(compound_cells, reverse=True)

    remaining_counts = sum(requires)
    max_possible_cells = 0

    # Take as many compounds as we have remaining blocks
    for c in compound_cells_sorted:
        if remaining_counts <= 0:
            break
        max_possible_cells += c
        remaining_counts -= 2  # each compound usually covers 2 objects

    # Add remaining single objects
    single_cells = sum(np.sum(p.detail) for p, count in zip(presents, requires))
    max_possible_cells += single_cells

    if max_possible_cells < total_cells:
        return False  # even with compound blocks, cannot fit

    # Passed all safe heuristics
    return True
# ----------------------------
# Top-level solve function
# ----------------------------
def solve12(presents, grid_defs):
    solvable = 0
    for grid in grid_defs:
        print(f"Solving grid id {grid[0]}")
        if  tetris_solver(grid[1],presents, grid[2]):
            solvable += 1
            print(f"found solution for {grid}")
        else:
            print(f"No solution for {grid}")
        
    return solvable

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
        # print(f"ID {tree_id}, tree size {tree_size}, requires {req_boxes}")
        grid_defs.append([tree_id, tree_size, req_boxes])
        tree_id +=1

    print(f"total solvable: {solve12(presents, grid_defs)}")

if __name__ == "__main__":
    main()


# # -----------------------
# # Example usage
# # -----------------------
# if __name__ == "__main__":
#     # 6 fixed 3x3 shapes
#     presents = [
#         Present(0, np.array([[1,1,1],[1,1,0],[1,1,0]], dtype=bool)),
#         Present(1, np.array([[1,1,1],[1,1,0],[0,1,1]], dtype=bool)),
#         Present(2, np.array([[0,1,1],[1,1,1],[1,1,0]], dtype=bool)),
#         Present(3, np.array([[1,1,0],[1,1,1],[1,1,0]], dtype=bool)),
#         Present(4, np.array([[1,1,1],[1,0,0],[1,1,1]], dtype=bool)),
#         Present(5, np.array([[1,1,1],[0,1,0],[1,1,1]], dtype=bool)),
#     ]

#     # Example grid + requirements
#     grid_shape = (12, 5)
#     requires = (1,0,1,0,3,2)

#     solvable = tetris_solver(grid_shape, presents, requires)
#     print(f"Solvable? {solvable}")

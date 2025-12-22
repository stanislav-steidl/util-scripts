import numpy as np
from dataclasses import dataclass
import dlx

@dataclass
class Present:
    id: int
    detail: np.ndarray

    def unique_variants(self):
        variants = [
            self.detail,
            np.rot90(self.detail, 1),
            np.rot90(self.detail, 2),
            np.rot90(self.detail, 3),
            np.fliplr(self.detail),
            np.flipud(self.detail),
            np.rot90(np.fliplr(self.detail)),
            np.rot90(np.flipud(self.detail)),
        ]
        seen = set()
        unique = []
        for v in variants:
            h = hash(v.tobytes())
            if h not in seen:
                seen.add(h)
                unique.append(v)
        return unique

def exact_cover_solver(H, W, presents, requires):
    # Columns: grid cells + present copies
    grid_cols = [(y, x) for y in range(H) for x in range(W)]
    present_cols = [(p.id, i) for p, r in zip(presents, requires) for i in range(r)]
    columns = grid_cols + present_cols
    col_index = {c:i for i, c in enumerate(columns)}
    num_cols = len(columns)

    # DLX requires columns as tuples (name, something)
    dlx_columns = [(c, None) for c in range(num_cols)]

    # Build rows
    rows = []
    for p_idx, p in enumerate(presents):
        variants = p.unique_variants()
        req_count = requires[p_idx]
        for copy_idx in range(req_count):
            for v in variants:
                h, w = v.shape
                for y in range(H - h + 1):
                    for x in range(W - w + 1):
                        cells = [(y+dy, x+dx) for dy in range(h) for dx in range(w) if v[dy,dx]]
                        if not cells:
                            continue
                        row = [col_index[c] for c in cells]
                        row.append(col_index[(p.id, copy_idx)])
                        rows.append(row)

    if not rows:
        return False

    # Solve using DLX
    solver = dlx.DLX(dlx_columns, rows=rows)
    
    # Iterate over solutions; stop at first one
    for solution in solver.solve():
        return True  # solution exists

    return False  # no solution found
# # -----------------------------
# # Example usage
# # -----------------------------
# if __name__ == "__main__":
#     # Example grid and requirements
#     H, W = 4,4
#     requires = [0,0,0,0,2,0]

#     # Define 6 presents (from your corrected list)
#     presents = [
#         Present(0, np.array([[False, True, True],[True, True, False],[True, False, False]])),
#         Present(1, np.array([[True, False, True],[True, True, True],[True, False, True]])),
#         Present(2, np.array([[True, True, True],[False, True, True],[False, False, True]])),
#         Present(3, np.array([[True, False, True],[True, True, True],[True, True, False]])),
#         Present(4, np.array([[True, True, True],[True, True, False],[True, True, False]])),
#         Present(5, np.array([[True, True, True],[True, False, True],[True, False, True]])),
#     ]

#     solver = ExactCoverSolver(H,W,presents,requires)
#     solvable = solver.solve()
#     print("Solvable?" , solvable)


def solve12(presents, grid_defs):
    total_solvable = 0
    for grid in grid_defs:
        tree_id, tree_size, req_boxes = grid
        print(f"Solving grid id {tree_id}")
        solvable = exact_cover_solver(tree_size[0],tree_size[1],presents,req_boxes)
        if  solvable:
            total_solvable += 1
            print(f"found solution for {grid}")
        else:
            print(f"No solution for {grid}")
        
    return total_solvable

def main():
    print("Day 12 Advent of Code 2025")
    with open("toy_problems/advent_of_code/aoc_2025/day12/data/toy.txt", "r") as f:
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
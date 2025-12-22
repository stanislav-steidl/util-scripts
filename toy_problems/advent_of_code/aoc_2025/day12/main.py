from tqdm import tqdm
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from ortools.sat.python import cp_model
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
        presents.append(Present(id,shape,detail_bool))
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


def solve12(presents, grid_defs):
    solvable = 0
    for grid in grid_defs:
        if grid_solvable(presents,grid):
            solvable +=1
    return solvable

        
def grid_solvable(presents,grid):
    H, W = grid[1]
    requires = grid[2]

    # ----------------------------
    # Create CP-SAT model
    # ----------------------------
    model = cp_model.CpModel()

    # Store variables for all copies
    placements = []
    for p_idx, p in enumerate(presents):
        variants = p.list_all_variants()
        for copy_idx in range(requires[p_idx]):
            var_dict = {}
            # Variant index 0..7
            var_dict['variant'] = model.NewIntVar(0, len(variants)-1, f'variant_{p.id}_{copy_idx}')
            # x, y positions
            var_dict['x'] = model.NewIntVar(0, W-1, f'x_{p.id}_{copy_idx}')
            var_dict['y'] = model.NewIntVar(0, H-1, f'y_{p.id}_{copy_idx}')
            placements.append((p, var_dict))

    
    # ----------------------------
    # Precompute sizes for each variant
    # ----------------------------
    variant_shapes = {}
    for p in presents:
        variant_shapes[p.id] = [v.shape for v in p.list_all_variants()]

    # ----------------------------
    # Add boundary constraints
    # ----------------------------
    for p, v in placements:
        # Width/height per variant
        # We must ensure x+width <= W, y+height <= H
        # Create intermediate variables to enforce constraints using Element constraints
        widths = [shape[1] for shape in variant_shapes[p.id]]
        heights = [shape[0] for shape in variant_shapes[p.id]]
        model.AddElement(v['variant'], widths, v['x'] + 1)  # x + width <= W → simplified later
        model.AddElement(v['variant'], heights, v['y'] + 1)

        # Bound x,y more strictly
        # Max width/height among variants
        max_w = max(widths)
        max_h = max(heights)
        model.Add(v['x'] <= W - max_w)
        model.Add(v['y'] <= H - max_h)

    # ----------------------------
    # Overlap constraints (naive cell-based)
    # ----------------------------
    # Create a grid of occupancy variables
    grid = {}
    for i in range(H):
        for j in range(W):
            grid[i,j] = model.NewBoolVar(f'cell_{i}_{j}')

    # Link placements to grid occupancy
    cell_vars = []
    for p, v in placements:
        variants_masks = p.list_all_variants()
        # one variable per copy per variant per mask cell
        vars_per_copy = []
        for variant_idx, mask in enumerate(variants_masks):
            h_mask, w_mask = mask.shape
            mask_cells = []
            for dy in range(h_mask):
                for dx in range(w_mask):
                    if mask[dy, dx]:
                        # create a boolean variable: does this placement occupy this cell?
                        bvar = model.NewBoolVar(f'p{p.id}_copy_{v}_v{variant_idx}_cell_{dy}_{dx}')
                        mask_cells.append((bvar, dx, dy, variant_idx))
            vars_per_copy.append(mask_cells)
        cell_vars.append(vars_per_copy)
    
        # If variant == variant_idx, then the cell is occupied
    for copy_idx, (p, v) in enumerate(placements):
        variants_masks = p.list_all_variants()
        for variant_idx, mask in enumerate(variants_masks):
            h_mask, w_mask = mask.shape
            for dy in range(h_mask):
                for dx in range(w_mask):
                    if mask[dy, dx]:
                        # If this variant is selected, then this cell is occupied at x+dx, y+dy
                        model.AddBoolOr([
                            v['variant'] != variant_idx,
                            # you would OR with some occupancy variable in global grid
                        ])
    # ----------------------------
    # Solve
    # ----------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 180.0

    status = solver.Solve(model)
    result = False
    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        result = True
        print("Solution found:")
        for p, v in placements:
            x = solver.Value(v['x'])
            y = solver.Value(v['y'])
            variant = solver.Value(v['variant'])
            print(f'Present {p.id} at ({x},{y}), variant {variant}')
    else:
        print("No solution found")


    return result



def can_place(bin_grid, obj_mask, x, y):
    h, w = obj_mask.shape
    if y+h > bin_grid.shape[0] or x+w > bin_grid.shape[1]:
        return False
    return not np.any(bin_grid[y:y+h, x:x+w] & obj_mask)

def place(bin_grid, obj_mask, x, y):
    h, w = obj_mask.shape
    bin_grid[y:y+h, x:x+w] |= obj_mask


@dataclass
class Present:
    id: int
    convex_hull: tuple[int, ...] # always 3x3
    detail: NDArray[np.bool_] 

    def list_all_variants(self):
        obj_mask = self.detail
        return  [
    obj_mask,                          # 0° original
    np.rot90(obj_mask),                # 90°
    np.rot90(obj_mask, 2),             # 180°
    np.rot90(obj_mask, 3),             # 270°
    np.fliplr(obj_mask),               # horizontal flip
    np.flipud(obj_mask),               # vertical flip
    np.rot90(np.fliplr(obj_mask)),     # horizontal flip + 90°
    np.rot90(np.flipud(obj_mask)),     # vertical flip + 90°
]



if __name__ == "__main__":
    main()
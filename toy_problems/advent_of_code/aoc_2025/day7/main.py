



def main():
    print("This is a placeholder for Day 7 solution.")

    #load dara from toy_problems/advent_of_code/aoc_2025/day7/data/input.txt such that every line is an element in a list of strings
    with open("toy_problems/advent_of_code/aoc_2025/day7/data/input.txt", 'r') as file:
    #with open("toy_problems/advent_of_code/aoc_2025/day7/data/toy.txt", 'r') as file:
        matrix_data = file.read().strip().splitlines()



    seed_beams = matrix_data[0]
    matrix_data = matrix_data[1:]
    for line in matrix_data:
        print(line)
    #matrix_data = [line.split() for line in data]
    splits = 0
    active_beams = [seed_beams.find("S")]
    for line in matrix_data:
        next_active_beams = []
        for active_beam in active_beams:
            if line[active_beam] == "^":
                splits += 1
                if active_beam - 1 >= 0:
                    next_active_beams.append(active_beam - 1)
                if active_beam + 1 < len(line):
                    next_active_beams.append(active_beam + 1)
            elif line[active_beam] == ".":
                next_active_beams.append(active_beam)
        active_beams = list(set(next_active_beams))
    print(f"Number of splits: {splits}")



    for line in matrix_data:
        print(line)
        
    #matrix_data = [line.split() for line in data]
    splits = 0
    active_beams = [seed_beams.find("S")]
    beam_strength = [0] * len(seed_beams)
    beam_strength[active_beams[0]] = 1
    for line in matrix_data:
        next_active_beams = []
        next_beam_strength = [0] * len(seed_beams)
        for i in range(len(beam_strength)):
            if beam_strength[i] > 0:
                active_beam = i
            else:
                continue

            if line[active_beam] == "^":
                splits += 1
                if active_beam - 1 >= 0:
                    next_beam_strength[active_beam - 1] += beam_strength[active_beam] 
                    next_active_beams.append(active_beam - 1)
                if active_beam + 1 < len(line):
                    next_beam_strength[active_beam + 1] += beam_strength[active_beam] 
                    next_active_beams.append(active_beam + 1)
            elif line[active_beam] == ".":
                next_active_beams.append(active_beam)
                next_beam_strength[active_beam] += beam_strength[active_beam] 
        active_beams = list(set(next_active_beams))
        beam_strength = next_beam_strength
    print("Beam strengths:", beam_strength)
    print("Total beam strength:", sum(beam_strength))
    print(f"Number of splits: {splits}")

                





if __name__ == "__main__":
    main()
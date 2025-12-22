

from toy_problems.advent_of_code.aoc_2025.utils import DataHandler
from toy_problems.advent_of_code.aoc_2025.data_types import SmallInt



def main_part1():
    
    loader = DataHandler("toy_problems/advent_of_code/aoc_2025/day1", 1)
    data: list[str] = loader.load_data()

    #PART 1
    safe_value = SmallInt(50)
    for line in data:
        letter, number = loader.parse_letter_and_number(line)
        if letter == 'R':
            safe_value += number
        elif letter == 'L':
            safe_value -= number

    zeroes = SmallInt.zero_counter
    print(f"Part 1: Total zeroes stopped: {zeroes}")

    #part 2
    passed_zeroes = SmallInt.passed_zeroes
    print(f"Part 2: Total zeroes encountered: {passed_zeroes}, total zeroes: {zeroes+passed_zeroes}")






if __name__ == "__main__":
    main_part1()


    
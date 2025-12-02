import random
from collections import Counter
import argparse
import matplotlib.pyplot as plt

# ----------------------------
# Dice simulation functions
# ----------------------------
def roll_die(n_sides=6):
    """Simulate a single dice roll."""
    return random.randint(1, n_sides)

def simulate_dice_tosses(num_rolls=1000, n_sides=6):
    """Simulate num_rolls dice tosses and return counts and probabilities."""
    results = [roll_die(n_sides) for _ in range(num_rolls)]
    counts = Counter(results)
    probabilities = {side: counts.get(side, 0)/num_rolls for side in range(1, n_sides+1)}
    return counts, probabilities

def plot_probabilities(probs):
    sides = list(probs.keys())
    values = list(probs.values())
    plt.bar(sides, values, color='skyblue')
    plt.xlabel("Dice Side")
    plt.ylabel("Probability")
    plt.title("Dice Toss Simulation Probabilities")
    plt.ylim(0, 1)
    plt.show()

# ----------------------------
# Main script with argparse
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="Dice Toss Simulation")
    parser.add_argument("--num-rolls", type=int, default=1000, help="Number of dice rolls")
    parser.add_argument("--sides", type=int, default=6, help="Number of sides on the dice")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--no-plot", action="store_true", help="Do not display the plot")
    
    args = parser.parse_args()

    # Set seed if provided
    if args.seed is not None:
        random.seed(args.seed)

    # Run simulation
    counts, probs = simulate_dice_tosses(num_rolls=args.num_rolls, n_sides=args.sides)
    print(f"Counts: {counts}")
    print(f"Probabilities: {probs}")

    # Plot if not disabled
    if not args.no_plot:
        plot_probabilities(probs)

if __name__ == "__main__":
    main()

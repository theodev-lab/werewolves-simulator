from config import ROLE_COUNTS, N_GAMES, SEED
from simulation.simulator import Simulator
from utils.stats import print_results
import sys

def main():
	if hasattr(sys.stdout, "reconfigure"):
		sys.stdout.reconfigure(encoding="utf-8")

	simulator = Simulator(ROLE_COUNTS, N_GAMES, seed=SEED)
	results = simulator.run()
    
	if N_GAMES > 1:
		print_results(results)
 
if __name__ == "__main__":
	main()

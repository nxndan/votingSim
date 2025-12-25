import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# main.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from election.generate import generate_election
from election.system import plurality_winner, borda_winner, irv_winner

def run_simulation(num_voters=100, num_candidates=4):
    ballots = generate_election(num_voters, num_candidates)

    p = plurality_winner(ballots)
    b = borda_winner(ballots)
    i = irv_winner(ballots)

    print("\nElection Results:")
    print("-----------------")
    print(f"Plurality winner: {p}")
    print(f"Borda Count winner: {b}")
    print(f"IRV winner: {i}")

if __name__ == "__main__":
    run_simulation()

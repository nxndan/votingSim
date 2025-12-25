# election/tests/demo_test.py

import sys, os
# optional fallback: add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ..generate import generate_election
from ..system import plurality_winner, borda_winner, irv_winner
from ..fairness import find_condorcet_winner, satisfaction_score

def test_small_ballots():
    ballots = [
        ['A', 'B', 'C'],
        ['A', 'C', 'B'],
        ['B', 'A', 'C'],
        ['C', 'A', 'B'],
        ['C', 'B', 'A']
    ]
    print("Ballots:", ballots)
    print("Plurality:", plurality_winner(ballots))
    print("Borda:", borda_winner(ballots))
    print("IRV:", irv_winner(ballots))
    print("Condorcet:", find_condorcet_winner(ballots))
    print("Satisfaction (Borda):", satisfaction_score(borda_winner, ballots))

if __name__ == "__main__":
    test_small_ballots()

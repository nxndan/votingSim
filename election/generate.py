import random

def generate_election(num_voters=100, num_candidates=4):
    candidates = [f"C{i}" for i in range(1, num_candidates + 1)]
    ballots = []
    for _ in range(num_voters):
        ballot = random.sample(candidates, len(candidates)) 
        ballots.append(ballot)
    return ballots
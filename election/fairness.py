# election/fairness.py
from collections import defaultdict
from copy import deepcopy
import random

# -------------------------------
# Pairwise comparisons
# -------------------------------
def pairwise_matrix(ballots):
    """
    Build a matrix (dict) of head-to-head wins: (a,b) -> # voters preferring a over b
    """
    if not ballots:
        return {}
    candidates = ballots[0]
    matrix = {}
    for a in candidates:
        for b in candidates:
            if a == b:
                continue
            matrix[(a, b)] = 0
    for ballot in ballots:
        for i, a in enumerate(ballot):
            for b in ballot[i + 1:]:
                matrix[(a, b)] += 1
    return matrix

# -------------------------------
# Condorcet Winner
# -------------------------------
def find_condorcet_winner(ballots):
    """
    Return the candidate that beats every other candidate head-to-head, if one exists.
    Otherwise return None.
    """
    matrix = pairwise_matrix(ballots)
    if not matrix:
        return None
    candidates = sorted(list({c for pair in matrix.keys() for c in pair}))
    for c in candidates:
        beats_all = True
        for other in candidates:
            if c == other:
                continue
            if matrix.get((c, other), 0) <= matrix.get((other, c), 0):
                beats_all = False
                break
        if beats_all:
            return c
    return None

# -------------------------------
# Satisfaction Score
# -------------------------------
def satisfaction_score(system_func, ballots):
    """
    Returns average satisfaction of voters with the winner.
    Winner ranked higher = higher satisfaction.
    Normalized between 0 (worst) and 1 (best).
    """
    if not ballots:
        return 0.0
    winner = system_func(ballots)
    if winner is None:
        return 0.0
    n = len(ballots[0])
    total = 0
    for b in ballots:
        rank = b.index(winner)
        total += (n - 1 - rank) / (n - 1)
    return total / len(ballots)

# -------------------------------
# Condorcet Compliance
# -------------------------------
def condorcet_compliance(system_func, ballots):
    """
    Returns True if system selects the Condorcet winner (when one exists).
    """
    cw = find_condorcet_winner(ballots)
    if cw is None:
        return None  # no Condorcet winner in this election
    winner = system_func(ballots)
    return cw == winner

# -------------------------------
# Monotonicity Test
# -------------------------------
def monotonicity_violation_rate(system_func, ballots, trials=30):
    """
    Approximate monotonicity test:
    - Pick random voter who doesn't rank winner 1st
    - Move winner up one rank
    - If the promoted candidate loses, count as violation
    Returns fraction of trials with violation.
    """
    if not ballots:
        return 0.0
    original_winner = system_func(ballots)
    if original_winner is None:
        return 0.0

    n = len(ballots)
    violations = 0
    for _ in range(trials):
        b_copy = deepcopy(ballots)
        # Pick voter who doesn’t have winner at top
        idxs = [i for i, b in enumerate(b_copy) if b.index(original_winner) > 0]
        if not idxs:
            break
        i = random.choice(idxs)
        pos = b_copy[i].index(original_winner)
        # Move up one spot
        b_copy[i][pos], b_copy[i][pos - 1] = b_copy[i][pos - 1], b_copy[i][pos]
        new_winner = system_func(b_copy)
        if new_winner != original_winner:
            violations += 1
    return violations / max(1, trials)

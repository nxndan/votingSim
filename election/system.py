from election.utils import count_first_choices, remove_candidate
from collections import defaultdict

# --- Plurality ---
def plurality_winner(ballots):
    tally = count_first_choices(ballots)
    return max(tally, key=tally.get)

# --- Borda Count ---
def borda_winner(ballots):
    scores = defaultdict(int)
    num_candidates = len(ballots[0])
    for ballot in ballots:
        for rank, candidate in enumerate(ballot):
            scores[candidate] += (num_candidates - rank - 1)
    return max(scores, key=scores.get)

# --- Instant Runoff Voting (IRV) ---
def irv_winner(ballots):
    ballots_copy = ballots.copy()
    while True:
        tally = count_first_choices(ballots_copy)
        # If one candidate has > 50% votes, they win
        total_votes = sum(tally.values())
        for candidate, votes in tally.items():
            if votes > total_votes / 2:
                return candidate
        # Eliminate candidate with fewest votes
        lowest = min(tally, key=tally.get)
        ballots_copy = remove_candidate(ballots_copy, lowest)
        if len(ballots_copy[0]) == 1:
            return ballots_copy[0][0]  # last one remaining

# --- Ranked Pairs (Tideman) ---
from collections import defaultdict

def ranked_pairs_winner(ballots):
    """
    Implements the Ranked Pairs (Tideman) voting method.
    It constructs pairwise victories and locks them to avoid cycles.
    """
    if not ballots:
        return None
    candidates = list(ballots[0])

    # Pairwise preferences
    pairwise = { (a,b): 0 for a in candidates for b in candidates if a != b }
    for ballot in ballots:
        for i_idx, i in enumerate(ballot):
            for j in ballot[i_idx+1:]:
                pairwise[(i,j)] += 1

    # Sort pairs by strength of victory
    pairs = []
    for a in candidates:
        for b in candidates:
            if a == b:
                continue
            a_over_b = pairwise.get((a,b), 0)
            b_over_a = pairwise.get((b,a), 0)
            if a_over_b > b_over_a:
                margin = a_over_b - b_over_a
                pairs.append((a, b, margin))
    pairs.sort(key=lambda x: -x[2])  # strongest victories first

    # Lock pairs avoiding cycles
    locked = {c: set() for c in candidates}

    def creates_cycle(start, end, graph):
        """Detect if adding a link start->end would create a cycle."""
        stack = [end]
        visited = set()
        while stack:
            node = stack.pop()
            if node == start:
                return True
            visited.add(node)
            for nxt in graph[node]:
                if nxt not in visited:
                    stack.append(nxt)
        return False

    for winner, loser, margin in pairs:
        if not creates_cycle(winner, loser, locked):
            locked[winner].add(loser)

    # Candidate with no incoming edges is the winner
    incoming = {c: 0 for c in candidates}
    for a in locked:
        for b in locked[a]:
            incoming[b] += 1

    zero_in = [c for c,v in incoming.items() if v == 0]
    return zero_in[0] if zero_in else None

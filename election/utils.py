from collections import Counter

def count_first_choices(ballots):
    """Return a Counter of first-choice votes for each candidate."""
    first_choices = [ballot[0] for ballot in ballots]
    return Counter(first_choices)

def remove_candidate(ballots, candidate):
    """Remove a candidate from all ballots."""
    new_ballots = []
    for ballot in ballots:
        new_ballots.append([c for c in ballot if c != candidate])
    return new_ballots
# election/data_collector.py
import csv, os
from tqdm import trange  # progress bar (pip install tqdm)
from election.generate import generate_election
from election.system import (
    plurality_winner,
    borda_winner,
    irv_winner,
    ranked_pairs_winner,
)
from election.fairness import (
    find_condorcet_winner,
    satisfaction_score,
    condorcet_compliance,
    monotonicity_violation_rate,
)

# ---------------------------------------------------
# Run repeated random elections and record statistics
# ---------------------------------------------------
def run_experiments(
    outfile="results.csv",
    num_trials=500,
    num_voters=200,
    num_candidates=4,
):
    systems = {
        "Plurality": plurality_winner,
        "Borda": borda_winner,
        "IRV": irv_winner,
        "RankedPairs": ranked_pairs_winner,
    }

    fieldnames = [
        "trial",
        "system",
        "satisfaction",
        "condorcet_compliance",
        "monotonicity_violation_rate",
    ]

    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", outfile)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in trange(num_trials, desc="Running simulations"):
            ballots = generate_election(num_voters, num_candidates)
            for name, func in systems.items():
                row = {
                    "trial": i + 1,
                    "system": name,
                    "satisfaction": satisfaction_score(func, ballots),
                    "condorcet_compliance": condorcet_compliance(func, ballots),
                    "monotonicity_violation_rate": monotonicity_violation_rate(
                        func, ballots, trials=10
                    ),
                }
                writer.writerow(row)

    print(f"\n✅ Data saved to {path}")
    return path


if __name__ == "__main__":
    run_experiments(num_trials=200)  # change to 1000+ later for full dataset

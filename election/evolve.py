# election/evolve.py
"""
Genetic algorithm to evolve positional scoring rules (weight vectors)
that maximize a combined fairness objective.
Run as: python -m election.evolve
"""

import random
import csv
import os
from statistics import mean
from copy import deepcopy

import numpy as np

from election.generate import generate_election
from election.fairness import (
    satisfaction_score,
    condorcet_compliance,
    find_condorcet_winner,
    monotonicity_violation_rate,
)
# We'll use a local apply_rule, not the system module, because evolved rules are custom.

# -------------------------
# Rule application
# -------------------------
def apply_rule(ballots, weights):
    """Apply a positional scoring rule defined by `weights` to ballots; return winner."""
    # weights: list length = num_candidates, index=rank (0=first)
    if not ballots:
        return None
    scores = {c: 0 for c in ballots[0]}
    for ballot in ballots:
        for rank, cand in enumerate(ballot):
            # if weights shorter, treat missing as 0
            val = weights[rank] if rank < len(weights) else 0
            scores[cand] += val
    return max(scores, key=scores.get)

# -------------------------
# Fitness evaluation
# -------------------------
def evaluate_rule(weights, num_trials=30, num_voters=100, num_candidates=4):
    """
    Returns a tuple: (fitness_scalar, avg_sat, condorcet_rate, avg_mono).
    """
    sats = []
    cond_hits = 0
    cond_exists = 0
    monos = []

    for _ in range(num_trials):
        ballots = generate_election(num_voters, num_candidates)
        # satisfaction for this rule
        sat = satisfaction_score(lambda b: apply_rule(b, weights), ballots)
        sats.append(sat)
        # condorcet
        cw = find_condorcet_winner(ballots)
        if cw is not None:
            cond_exists += 1
            if condorcet_compliance(lambda b: apply_rule(b, weights), ballots):
                cond_hits += 1
        # monotonicity
        mono = monotonicity_violation_rate(lambda b: apply_rule(b, weights), ballots, trials=10)
        monos.append(mono)

    avg_sat = mean(sats) if sats else 0.0
    cond_rate = (cond_hits / cond_exists) if cond_exists > 0 else 0.0
    avg_mono = mean(monos) if monos else 0.0

    # Weighted objective: tune these coefficients as you like
    fitness = 0.6 * avg_sat + 0.3 * cond_rate - 0.1 * avg_mono
    return fitness, avg_sat, cond_rate, avg_mono

# -------------------------
# GA helpers
# -------------------------
def random_rule(num_candidates, max_weight=10):
    """Return a nonincreasing integer vector length num_candidates."""
    v = [random.randint(0, max_weight) for _ in range(num_candidates)]
    v.sort(reverse=True)
    return v

def mutate_rule(rule, mutation_rate=0.3, max_step=2):
    child = rule[:]
    for i in range(len(child)):
        if random.random() < mutation_rate:
            child[i] = max(0, child[i] + random.choice([-max_step, -1, 0, 1, max_step]))
    child.sort(reverse=True)
    return child

def crossover(parent_a, parent_b):
    """One-point crossover (deterministic length)"""
    n = len(parent_a)
    if n <= 1:
        return parent_a[:]
    pt = random.randint(1, n - 1)
    child = parent_a[:pt] + parent_b[pt:]
    child.sort(reverse=True)
    return child

# -------------------------
# Main GA loop
# -------------------------
def evolve_rules(
    generations=40,
    population_size=20,
    num_candidates=4,
    num_trials=30,
    num_voters=100,
    mutation_rate=0.3,
    elitism_frac=0.3,
    log_csv="data/evolve_log.csv",
    seed=None,
):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    os.makedirs("data", exist_ok=True)

    # Initialize population
    population = [random_rule(num_candidates, max_weight=10) for _ in range(population_size)]

    # CSV logging
    with open(log_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["generation", "rank", "weights", "fitness", "avg_sat", "cond_rate", "avg_mono"])

    best_overall = None
    best_overall_score = -1e9

    for gen in range(1, generations + 1):
        print(f"\n=== Starting Generation {gen}/{generations} ===")
        scored = []
        for rule in population:
            fitness, avg_sat, cond_rate, avg_mono = evaluate_rule(rule, num_trials=num_trials, num_voters=num_voters, num_candidates=num_candidates)
            scored.append((rule, fitness, avg_sat, cond_rate, avg_mono))
            print(f"  → Evaluated rule {rule} → fitness {fitness:.3f}")

        # sort by fitness desc
        scored.sort(key=lambda x: x[1], reverse=True)

        # logging
        with open(log_csv, "a", newline="") as f:
            writer = csv.writer(f)
            for rank, (rule, fitness, avg_sat, cond_rate, avg_mono) in enumerate(scored, start=1):
                writer.writerow([gen, rank, rule, fitness, avg_sat, cond_rate, avg_mono])

        best_rule, best_score, best_sat, best_cond, best_mono = scored[0]
        avg_gen_score = mean([s for (_, s, _, _, _) in scored])

        print(f"Gen {gen}/{generations} — Best {best_rule} → fitness {best_score:.4f} (sat {best_sat:.3f}, cond {best_cond:.3f}, mono {best_mono:.3f}) — avg {avg_gen_score:.4f}")

        if best_score > best_overall_score:
            best_overall_score = best_score
            best_overall = deepcopy(best_rule)

        # Selection: keep top K parents
        k = max(1, int(elitism_frac * population_size))
        parents = [r for (r, _, _, _, _) in scored[:k]]

        # Reproduce children until full population
        new_pop = parents[:]
        while len(new_pop) < population_size:
            a = random.choice(parents)
            b = random.choice(parents)
            child = crossover(a, b)
            child = mutate_rule(child, mutation_rate=mutation_rate)
            new_pop.append(child)

        population = new_pop

    # Final evaluation of best overall
    final_fitness, final_sat, final_cond, final_mono = evaluate_rule(best_overall, num_trials=100, num_voters=num_voters, num_candidates=num_candidates)
    print("\n=== FINAL BEST RULE ===")
    print("Weights (rank1→...):", best_overall)
    print(f"Fitness: {final_fitness:.4f}, sat: {final_sat:.4f}, cond_rate: {final_cond:.4f}, mono: {final_mono:.4f}")

    # Save best rule
    best_path = os.path.join("data", "best_rule.txt")
    with open(best_path, "w") as f:
        f.write(f"{best_overall}\nfitness:{final_fitness:.6f}\nsat:{final_sat:.6f}\ncond_rate:{final_cond:.6f}\nmono:{final_mono:.6f}\n")
    print(f"Best rule saved to {best_path}")

    return best_overall, final_fitness, final_sat, final_cond, final_mono

# -------------------------
# If run as module
# -------------------------
if __name__ == "__main__":
    # short default run for quick testing; bump values for full runs
    best = evolve_rules(
        generations=20,
        population_size=15,
        num_candidates=4,
        num_trials=25,
        num_voters=120,
        mutation_rate=0.3,
        elitism_frac=0.3,
        log_csv="data/evolve_log.csv",
        seed=42,
    )

import os
import random
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

# Base directory = folder where this script lives
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Build paths relative to the script location
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")


def load_csv(filename: str) -> pd.DataFrame:
    """Load a CSV from the data/processed folder."""
    path = os.path.join(DATA_DIR, filename)
    return pd.read_csv(path)


teams = load_csv("field68_with_strength.csv")
bracket = load_csv("bracket_structure.csv")

teams["ZRating"] = (
    (teams["NetRating"] - teams["NetRating"].mean()) /
    teams["NetRating"].std()
)

z_ratings = teams.set_index("Team")["ZRating"].to_dict()


def win_prob(a: str, b: str, ratings: dict = z_ratings, k: float = 1.33) -> float:
    """Return probability that team a beats team b."""
    if a not in ratings:
        raise ValueError(f"{a} not found in ratings")
    if b not in ratings:
        raise ValueError(f"{b} not found in ratings")

    diff = ratings[a] - ratings[b]
    return 1 / (1 + np.exp(-k * diff))


def simulate_game(team_a: str, team_b: str) -> str:
    """Simulate one game and return the winner."""
    p_a = win_prob(team_a, team_b)
    return team_a if random.random() < p_a else team_b


def resolve_source(source, results: dict):
    """Resolve either a team name or a winner_x reference."""
    if isinstance(source, str) and source.startswith("winner_"):
        game_id = int(source.split("_")[1])
        return results[game_id]
    return source


def simulate_tournament(bracket_df: pd.DataFrame) -> dict:
    """Simulate the full tournament and return winners by game_id."""
    results = {}
    games_sorted = bracket_df.sort_values(["round", "game_id"])

    for _, game in games_sorted.iterrows():
        left_team = resolve_source(game["left_source"], results)
        right_team = resolve_source(game["right_source"], results)

        winner = simulate_game(left_team, right_team)
        results[game["game_id"]] = winner

    return results


def monte_carlo_sim(bracket_df: pd.DataFrame, n_sims: int = 10000) -> pd.DataFrame:
    """Estimate championship probabilities."""
    champion_counts = Counter()

    for _ in range(n_sims):
        results = simulate_tournament(bracket_df)
        champion = results[63]  # final game
        champion_counts[champion] += 1

    return pd.DataFrame({
        "Team": champion_counts.keys(),
        "Championship_Prob": [count / n_sims for count in champion_counts.values()]
    }).sort_values("Championship_Prob", ascending=False)


def monte_carlo_rounds(bracket_df: pd.DataFrame, n_sims: int = 10000) -> pd.DataFrame:
    """Estimate round advancement probabilities for every team."""
    round_counts = defaultdict(int)

    # Faster lookup instead of filtering bracket_df every loop
    round_lookup = bracket_df.set_index("game_id")["round"].to_dict()

    for _ in range(n_sims):
        results = simulate_tournament(bracket_df)

        for game_id, winner in results.items():
            round_num = round_lookup[game_id]
            round_counts[(winner, round_num)] += 1

    rows = []
    teams_list = sorted(z_ratings.keys())

    for team in teams_list:
        rows.append({
            "Team": team,
            "Round_1_Win": round_counts[(team, 1)] / n_sims,
            "Round_2_Win": round_counts[(team, 2)] / n_sims,
            "Sweet_16": round_counts[(team, 3)] / n_sims,
            "Elite_8": round_counts[(team, 4)] / n_sims,
            "Final_4": round_counts[(team, 5)] / n_sims,
            "Champion": round_counts[(team, 6)] / n_sims,
        })

    return pd.DataFrame(rows).sort_values("Champion", ascending=False)


advancement_probs = monte_carlo_rounds(bracket, n_sims=10000)
print(advancement_probs.head(20))

current_teams = load_csv("field68_with_strength.csv")
print(current_teams.columns)

merged = advancement_probs.merge(
    current_teams[["Team", "Seed"]],
    on="Team"
)

public = load_csv("public_champ_odds.csv")

ev_df = merged.merge(public, on="Team", how="left")
ev_df["Public_Champ"] = ev_df["Public_Champ"].fillna(0)
ev_df["Champ_EV"] = ev_df["Champion"] * (1 - ev_df["Public_Champ"])
ev_df = ev_df.sort_values("Champ_EV", ascending=False)

print(ev_df.head(20))

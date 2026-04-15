import os
import pandas as pd


# Base directory = folder where this script lives
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Relative paths
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def load_csv(folder: str, filename: str) -> pd.DataFrame:
    """Load a CSV file from a specified folder."""
    path = os.path.join(folder, filename)
    return pd.read_csv(path)


def calculate_edges(model_df: pd.DataFrame, public_df: pd.DataFrame) -> pd.DataFrame:
    """Merge model and public data to compute probability edges."""
    
    model_df = model_df[["Team", "Champion"]]
    public_df = public_df[["Team", "Public_Champ"]]

    merged = pd.merge(model_df, public_df, on="Team", how="inner")

    merged = merged.rename(columns={
        "Champion": "model_prob",
        "Public_Champ": "public_prob"
    })

    merged["edge"] = merged["model_prob"] - merged["public_prob"]
    merged["edge_pct"] = merged["edge"] * 100

    merged["model_rank"] = merged["model_prob"].rank(ascending=False, method="min")
    merged["public_rank"] = merged["public_prob"].rank(ascending=False, method="min")
    merged["edge_rank"] = merged["edge"].rank(ascending=False, method="min")

    merged["valuation"] = merged["edge"].apply(
        lambda x: "Undervalued" if x > 0 else "Overvalued"
    )

    merged["model_prob"] = merged["model_prob"].round(4)
    merged["public_prob"] = merged["public_prob"].round(4)
    merged["edge"] = merged["edge"].round(4)
    merged["edge_pct"] = merged["edge_pct"].round(2)

    merged = merged.sort_values(by="edge", ascending=False).reset_index(drop=True)

    final_df = merged[
        [
            "Team",
            "model_prob",
            "public_prob",
            "edge",
            "edge_pct",
            "model_rank",
            "public_rank",
            "edge_rank",
            "valuation",
        ]
    ]

    return final_df


def main():
    """Run edge calculation and export results."""

    model_df = load_csv(OUTPUTS_DIR, "championship_probs.csv")
    public_df = load_csv(DATA_DIR, "public_champ_odds.csv")

    final_df = calculate_edges(model_df, public_df)

    # Save output
    output_path = os.path.join(OUTPUTS_DIR, "championship_edges.csv")
    final_df.to_csv(output_path, index=False)

    # Print preview
    print(final_df.head(20))
    print(f"\nSaved results to: {output_path}")


if __name__ == "__main__":
    main()
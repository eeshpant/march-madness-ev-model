# March Madness Monte Carlo Simulation

## Overview
I built a Monte Carlo simulation of the NCAA tournament to estimate how often each team advances and wins the championship. Instead of just predicting winners, the goal was to understand probabilities and where the public might be over- or under-valuing teams in bracket pools.

## Key Results
- Identified teams the public significantly overvalued relative to model probabilities
- Highlighted lower-owned teams with positive edge in bracket pools
- Showed how small probability differences can create leverage in large pools

## Method
- Team strength is based on net rating, normalized using a z-score
- Games are simulated using a logistic win probability function
- k = 1.33, which gives a more realistic upset rate based on past tournaments
- The full bracket is simulated 10,000 times

## What this produces
- Championship probabilities for each team
- Round-by-round advancement probabilities
- A comparison between model probabilities and public pick rates

## Edge calculation
I compare model probabilities to public pick percentages:

```
edge = model_prob - public_prob
```

Positive edge = undervalued team  
Negative edge = overvalued team  

This gives a simple way to think about leverage in bracket pools.

## Project structure
data/
  processed/
    field68_with_strength.csv
    bracket_structure.csv
    public_champ_odds.csv
  raw/
    2026_team_results.csv
    cbb.csv

outputs/
  championship_edges.csv
  championship_probs.csv
  model_info.json

src/
  simulate.py
  run_pool_ev.py


## How to run

Install dependencies:
```
pip install -r requirements.txt
```

Run the simulation:
```
python src/simulate.py
```

Run the edge calculation:
```
python src/run_pool_ev.py
```

## Limitations
- No matchup adjustments (style, injuries, etc.)
- Team strength is static throughout the tournament
- Edge is a simple proxy, not a full expected value model

## Next steps
- Add matchup-level adjustments
- Build a full bracket EV optimizer
- Improve calibration using historical data

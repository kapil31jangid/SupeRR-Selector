import pandas as pd
import numpy as np

# Load v3 season features (all competition)
bat_season = pd.read_csv('data/processed_v3/all_competition_batter_season_features.csv', low_memory=False)
bowl_season = pd.read_csv('data/processed_v3/all_competition_bowler_season_features.csv', low_memory=False)

# Load v3 scores
bat_scores = pd.read_csv('outputs/rankings_v3/preliminary_all_competition_batter_scores_v3.csv')
bowl_scores = pd.read_csv('outputs/rankings_v3/preliminary_all_competition_bowler_scores_v3.csv')

# Merge scores with season features for evidence scenario
# Exclude min_balls columns from scores to avoid duplicate column conflict
bat_ev = bat_scores[bat_scores['scenario'] == 'evidence'][['striker_id', 'season', 'composite_score', 'rank_evidence']].copy()
bowl_ev = bowl_scores[bowl_scores['scenario'] == 'evidence'][['bowler_id', 'season', 'composite_score', 'rank_evidence']].copy()

bat_merged = bat_ev.merge(bat_season, on=['striker_id', 'season'], how='left')
bowl_merged = bowl_ev.merge(bowl_season, on=['bowler_id', 'season'], how='left')

bat_elig = bat_merged[bat_merged['min_balls_100']].copy()
bowl_elig = bowl_merged[bowl_merged['min_balls_100']].copy()

print('=== BATTER RELIABILITY AUDIT (Evidence-Based, 100+ balls) ===')
print(f'Total eligible batters: {len(bat_elig)}')

# Sample size distribution
print(f'\nBalls faced distribution:')
print(bat_elig['total_balls'].describe())

# Pressure opportunity distribution
print(f'\nPressure opportunity distribution:')
print(f'  High+Extreme balls median: {bat_elig["high_extreme_balls"].median():.0f}')
print(bat_elig['high_extreme_balls'].describe())
print(f'  Chase balls median: {bat_elig["chase_balls"].median():.0f}')
print(bat_elig['chase_balls'].describe())
print(f'  Powerplay balls median: {bat_elig["powerplay_balls"].median():.0f}')
print(bat_elig['powerplay_balls'].describe())
print(f'  Death balls median: {bat_elig["death_balls"].median():.0f}')
print(bat_elig['death_balls'].describe())

# Flag low pressure opportunities
low_he = bat_elig[bat_elig['high_extreme_balls'] < 30]
low_chase = bat_elig[bat_elig['chase_balls'] < 30]
low_pp = bat_elig[bat_elig['powerplay_balls'] < 30]
low_death = bat_elig[bat_elig['death_balls'] < 30]
print(f'\nBatters with <30 High+Extreme balls: {len(low_he)} ({len(low_he)/len(bat_elig)*100:.1f}%)')
print(f'Batters with <30 Chase balls: {len(low_chase)} ({len(low_chase)/len(bat_elig)*100:.1f}%)')
print(f'Batters with <30 Powerplay balls: {len(low_pp)} ({len(low_pp)/len(bat_elig)*100:.1f}%)')
print(f'Batters with <30 Death balls: {len(low_death)} ({len(low_death)/len(bat_elig)*100:.1f}%)')

# Shrinkage effect
print('\n=== SHRINKAGE EFFECT (Evidence scenario) ===')
print('Strike rate:')
print(f'  Raw median: {bat_elig["strike_rate"].median():.1f}')
print(f'  Comp adj median: {bat_elig["strike_rate_comp_adj"].median():.1f}')
print(f'  Shrinkage adj median: {bat_elig["strike_rate_adj"].median():.1f}')

if 'high_extreme_sr' in bat_elig.columns:
    print('High Extreme SR:')
    print(f'  Raw median: {bat_elig["high_extreme_sr"].median():.1f}')
    print(f'  Shrinkage adj median: {bat_elig["high_extreme_sr_adj"].median():.1f}')

print('\n=== BOWLER RELIABILITY AUDIT (Evidence-Based, 100+ balls) ===')
print(f'Total eligible bowlers: {len(bowl_elig)}')

print(f'\nBalls bowled distribution:')
print(bowl_elig['total_balls'].describe())

print(f'\nPressure opportunity distribution:')
print(f'  High+Extreme balls median: {bowl_elig["high_extreme_balls"].median():.0f}')
print(bowl_elig['high_extreme_balls'].describe())
print(f'  Defend balls median: {bowl_elig["defend_balls"].median():.0f}')
print(bowl_elig['defend_balls'].describe())
print(f'  Powerplay balls median: {bowl_elig["powerplay_balls"].median():.0f}')
print(bowl_elig['powerplay_balls'].describe())
print(f'  Death balls median: {bowl_elig["death_balls"].median():.0f}')
print(bowl_elig['death_balls'].describe())

low_he_b = bowl_elig[bowl_elig['high_extreme_balls'] < 30]
low_def = bowl_elig[bowl_elig['defend_balls'] < 30]
low_pp_b = bowl_elig[bowl_elig['powerplay_balls'] < 30]
low_death_b = bowl_elig[bowl_elig['death_balls'] < 30]
print(f'\nBowlers with <30 High+Extreme balls: {len(low_he_b)} ({len(low_he_b)/len(bowl_elig)*100:.1f}%)')
print(f'Bowlers with <30 Defend balls: {len(low_def)} ({len(low_def)/len(bowl_elig)*100:.1f}%)')
print(f'Bowlers with <30 Powerplay balls: {len(low_pp_b)} ({len(low_pp_b)/len(bowl_elig)*100:.1f}%)')
print(f'Bowlers with <30 Death balls: {len(low_death_b)} ({len(low_death_b)/len(bowl_elig)*100:.1f}%)')

# Shrinkage effect
print('\n=== SHRINKAGE EFFECT (Bowler Evidence scenario) ===')
print('Economy rate:')
print(f'  Raw median: {bowl_elig["economy_rate"].median():.2f}')
print(f'  Comp adj median: {bowl_elig["economy_rate_comp_adj"].median():.2f}')
print(f'  Shrinkage adj median: {bowl_elig["economy_rate_adj"].median():.2f}')

print('Wicket rate:')
print(f'  Raw median: {bowl_elig["wicket_rate"].median():.4f}')
print(f'  Comp adj median: {bowl_elig["wicket_rate_comp_adj"].median():.4f}')
print(f'  Shrinkage adj median: {bowl_elig["wicket_rate_adj"].median():.4f}')

# Top 10 batters - check pressure opportunities
print('\n=== TOP 10 BATTERS PRESSURE OPPORTUNITIES ===')
top10_bat = bat_elig.nsmallest(10, 'rank_evidence')
for _, row in top10_bat.iterrows():
    print(f'  Rank {int(row["rank_evidence"])}: {row["striker_name"]} ({row["season"]}) - Balls: {row["total_balls"]:.0f}, HE: {row["high_extreme_balls"]:.0f}, Chase: {row["chase_balls"]:.0f}, PP: {row["powerplay_balls"]:.0f}, Death: {row["death_balls"]:.0f}')

# Top 10 bowlers
print('\n=== TOP 10 BOWLERS PRESSURE OPPORTUNITIES ===')
top10_bowl = bowl_elig.nsmallest(10, 'rank_evidence')
for _, row in top10_bowl.iterrows():
    print(f'  Rank {int(row["rank_evidence"])}: {row["bowler_name"]} ({row["season"]}) - Balls: {row["total_balls"]:.0f}, HE: {row["high_extreme_balls"]:.0f}, Def: {row["defend_balls"]:.0f}, PP: {row["powerplay_balls"]:.0f}, Death: {row["death_balls"]:.0f}')

# Seasons played
print('\n=== SEASONS PLAYED ===')
print(f'Batters median seasons: {bat_elig["seasons_played"].median()}')
print(f'Bowlers median seasons: {bowl_elig["seasons_played"].median()}')

# Check for single-season wonders in top 10
print('\n=== SINGLE SEASON PLAYERS IN TOP 10 ===')
for _, row in top10_bat.iterrows():
    if row['seasons_played'] == 1:
        print(f'  BATTER: {row["striker_name"]} ({row["season"]}) - Only 1 season, Score: {row["composite_score"]:.1f}')
for _, row in top10_bowl.iterrows():
    if row['seasons_played'] == 1:
        print(f'  BOWLER: {row["bowler_name"]} ({row["season"]}) - Only 1 season, Score: {row["composite_score"]:.1f}')
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint
from scipy.stats import fisher_exact

# ============================================================
# 0. PATHS AND SETTINGS
# ============================================================

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()  # fallback when running cell-by-cell (F9) in Spyder

# CSVs live in a "csv_euroleague" folder at the same level as the project
DATA_DIR = os.path.join(BASE_DIR, "..", "csv_euroleague")

IMAGES_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

QUARTER_ORDER = {'q1': 1, 'q2': 2, 'q3': 3, 'q4': 4, 'extra_time': 5}
DEFICIT_THRESHOLD = -15
HOT_ARENA_TEAMS = ['PAN', 'PAR', 'RED', 'BAS', 'ZAL']

TEAM_NAMES = {
    'PAR': 'Partizan',
    'PAN': 'Panathinaikos',
    'BAS': 'Baskonia',
    'RED': 'Crvena Zvezda',
    'ZAL': 'Zalgiris'
}

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)

# ============================================================
# 1. LOAD DATA
# ============================================================

header = pd.read_csv(os.path.join(DATA_DIR, "euroleague_header.csv"))
pbp = pd.read_csv(
    os.path.join(DATA_DIR, "euroleague_play_by_play.csv"),
    usecols=['game_id', 'quarter', 'number_of_play', 'points_a', 'points_b']
)

# ============================================================
# 2. RECONSTRUCT THE SCORE ALONG EACH GAME
# ============================================================

pbp['quarter_order'] = pbp['quarter'].map(QUARTER_ORDER)
pbp = pbp.sort_values(['game_id', 'quarter_order', 'number_of_play']).reset_index(drop=True)

# Forward-fill scores within each game (non-scoring plays do not update points_a/points_b)
pbp[['points_a', 'points_b']] = pbp.groupby('game_id')[['points_a', 'points_b']].ffill()
pbp[['points_a', 'points_b']] = pbp[['points_a', 'points_b']].fillna(0)

pbp['deficit_home'] = pbp['points_a'] - pbp['points_b']

# ============================================================
# 2.1 DATA QUALITY CHECKS ON THE RECONSTRUCTED SCORE
# ============================================================

print("=== Check 1: quarter labels ===")
print(pbp['quarter'].value_counts(dropna=False))
print(f"Plays with an unrecognised quarter label: {pbp['quarter_order'].isna().sum()}")

print("\n=== Check 2: coverage ===")
print(f"Games in the header: {header['game_id'].nunique()} | games in the play-by-play: {pbp['game_id'].nunique()}")

print("\n=== Check 3: reconstructed final score vs official final score ===")
last_play = pbp.groupby('game_id').tail(1).set_index('game_id')[['points_a', 'points_b']]
final_check = header.set_index('game_id')[['score_a', 'score_b']].join(last_play, how='inner')
score_mismatch = (final_check['score_a'] != final_check['points_a']) | (final_check['score_b'] != final_check['points_b'])
print(f"Games with a different final score: {score_mismatch.sum()} of {len(final_check)} ({score_mismatch.mean() * 100:.1f}%)")

print("\n=== Check 4: score going down during a game ===")
score_steps = pbp.groupby('game_id')[['points_a', 'points_b']].diff()
decreasing_games = set(pbp.loc[(score_steps['points_a'] < 0) | (score_steps['points_b'] < 0), 'game_id'])
print(f"Games where a team's score decreases at some point: {len(decreasing_games)}")

# Games with an inconsistent score path. They stay in the main analysis,
# and a robustness check without them is printed below.
flagged_games = set(final_check.index[score_mismatch]) | decreasing_games
print(f"Games with an inconsistent score path (either check): {len(flagged_games)}")

# ============================================================
# 3. WORST DEFICIT AND COMEBACK, FOR EVERY GAME
# From the point of the worst deficit onward, a comeback means that the team
# tied the score or took the lead at least once before the final buzzer.
# ============================================================

def analyze_game_full(group):
    """For one game: worst deficit from the home and the away team's perspective,
    and whether each team tied or led afterward."""
    deficit_home = group['deficit_home'].values

    idx_home = deficit_home.argmin()
    idx_away = (-deficit_home).argmin()

    return pd.Series({
        'worst_deficit_home': deficit_home[idx_home],
        'comeback_home': bool((deficit_home[idx_home:] >= 0).any()),
        'worst_deficit_away': (-deficit_home)[idx_away],
        'comeback_away': bool(((-deficit_home)[idx_away:] >= 0).any())
    })

print("\nProcessing all EuroLeague games, this may take a few seconds...")
league_results = pbp.groupby('game_id')[['deficit_home']].apply(analyze_game_full).reset_index()
print("Done.")

league_results = league_results.merge(
    header[['game_id', 'season_code', 'team_id_a', 'team_id_b']],
    on='game_id',
    how='left'
)

# ============================================================
# 4. RESHAPE TO LONG FORMAT (one row per team per game, with venue)
# Team A is the home team.
# ============================================================

home_side = league_results[['game_id', 'team_id_a', 'worst_deficit_home', 'comeback_home']].rename(
    columns={'team_id_a': 'team_id', 'worst_deficit_home': 'worst_deficit', 'comeback_home': 'comeback'}
)
home_side['venue'] = 'Home'

away_side = league_results[['game_id', 'team_id_b', 'worst_deficit_away', 'comeback_away']].rename(
    columns={'team_id_b': 'team_id', 'worst_deficit_away': 'worst_deficit', 'comeback_away': 'comeback'}
)
away_side['venue'] = 'Away'

team_long = pd.concat([home_side, away_side], ignore_index=True)

# ============================================================
# 5. COMEBACK RATE, PER TEAM, PER VENUE, WITH 95% INTERVALS
# Each row is a different game for a given team and venue, so the rows are independent
# and a Wilson interval applies to the rate.
# ============================================================

def summarize(df, by):
    out = df.groupby(by)['comeback'].agg(['sum', 'count']).reset_index()
    out['comeback_rate_pct'] = out['sum'] / out['count'] * 100
    lo, hi = proportion_confint(out['sum'], out['count'], alpha=0.05, method='wilson')
    out['ci_low'] = lo * 100
    out['ci_high'] = hi * 100
    return out

big_deficit = team_long[team_long['worst_deficit'] <= DEFICIT_THRESHOLD].copy()

league_summary = summarize(big_deficit, 'venue').set_index('venue')
hot_deficit = big_deficit[big_deficit['team_id'].isin(HOT_ARENA_TEAMS)]
hot_summary = summarize(hot_deficit, ['team_id', 'venue'])

print("\n=== League average (all teams, 15+ point deficit) ===")
print(league_summary.round(1))
print("\n=== Hot arena teams ===")
print(hot_summary.round(1))

# Robustness: same rates without games that have an inconsistent score path
clean_deficit = big_deficit[~big_deficit['game_id'].isin(flagged_games)]
print("\n=== Robustness: league and hot arena rates without the flagged games ===")
print(summarize(clean_deficit, 'venue').round(1))
print(summarize(clean_deficit[clean_deficit['team_id'].isin(HOT_ARENA_TEAMS)], ['team_id', 'venue']).round(1))

# ============================================================
# 6. HOME MINUS AWAY GAP, WITH BOOTSTRAP INTERVALS
# Every team has a home advantage in comebacks, so each team's gap is read against the league gap.
# Home and away games are resampled separately.
# ============================================================

rng = np.random.default_rng(42)
N_BOOT = 5000

def gap_with_interval(home_flags, away_flags):
    home_flags = np.asarray(home_flags, dtype=float)
    away_flags = np.asarray(away_flags, dtype=float)
    point = (home_flags.mean() - away_flags.mean()) * 100
    draws = np.empty(N_BOOT)
    for i in range(N_BOOT):
        h = home_flags[rng.integers(0, len(home_flags), len(home_flags))]
        a = away_flags[rng.integers(0, len(away_flags), len(away_flags))]
        draws[i] = (h.mean() - a.mean()) * 100
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return point, lo, hi

league_gap = gap_with_interval(
    big_deficit.loc[big_deficit['venue'] == 'Home', 'comeback'],
    big_deficit.loc[big_deficit['venue'] == 'Away', 'comeback']
)
print(f"\nLeague home minus away gap: {league_gap[0]:+.1f} points, 95% interval [{league_gap[1]:+.1f}, {league_gap[2]:+.1f}]")

gap_rows = []
for team in HOT_ARENA_TEAMS:
    t = hot_deficit[hot_deficit['team_id'] == team]
    home_f = t.loc[t['venue'] == 'Home', 'comeback']
    away_f = t.loc[t['venue'] == 'Away', 'comeback']
    point, lo, hi = gap_with_interval(home_f, away_f)

    # Fisher's exact test on the 2x2 table (home/away by comeback yes/no)
    table = [[home_f.sum(), len(home_f) - home_f.sum()], [away_f.sum(), len(away_f) - away_f.sum()]]
    _, p_value = fisher_exact(table)

    gap_rows.append({
        'team': TEAM_NAMES[team], 'home_games': len(home_f), 'away_games': len(away_f),
        'gap': point, 'gap_low': lo, 'gap_high': hi, 'fisher_p': p_value
    })

gap_table = pd.DataFrame(gap_rows).set_index('team')
print("\n=== Home minus away gap in comeback rate, per team (points) ===")
print(gap_table.round(3))

# ============================================================
# 7. SEASON COVERAGE CHECK (sample comparability across teams)
# ============================================================

print("\n=== Season coverage per team (seasons with games in the dataset) ===")
print(f"League: {header['season_code'].nunique()} seasons, {header['season_code'].min()} to {header['season_code'].max()}")
seasons_per_team = {}
for team in HOT_ARENA_TEAMS:
    team_seasons = sorted(set(header.loc[header['team_id_a'] == team, 'season_code'])
                          | set(header.loc[header['team_id_b'] == team, 'season_code']))
    seasons_per_team[team] = len(team_seasons)
    print(f"{team}: {len(team_seasons)} seasons, {team_seasons}")

# ============================================================
# 8. PLOT: HOT ARENA TEAMS vs LEAGUE AVERAGE, HOME/AWAY (light palette)
# Bars: comeback rate. Dark lines: 95% Wilson interval. Dashed line: league average.
# ============================================================

BG_COLOR = '#FBFCEE'      # figure and axes background
BORDER_COLOR = '#D6DFA8'  # spines and grid
TEXT_COLOR = '#16233F'    # titles, labels, ticks
BAR_COLOR = '#3E8E4F'     # green
LEAGUE_COLOR = '#C6564F'  # coral

home_order = (hot_summary[hot_summary['venue'] == 'Home']
              .sort_values('comeback_rate_pct', ascending=False)['team_id'].tolist())
ordered_labels = [f"{TEAM_NAMES[t]}\n({seasons_per_team[t]} seasons)" for t in home_order]

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.patch.set_facecolor(BG_COLOR)

for ax, venue_label in zip(axes, ['Home', 'Away']):
    ax.set_facecolor(BG_COLOR)
    sub = hot_summary[hot_summary['venue'] == venue_label].set_index('team_id').loc[home_order]
    league_val = league_summary.loc[venue_label, 'comeback_rate_pct']

    x = np.arange(len(home_order))
    ax.bar(x, sub['comeback_rate_pct'], color=BAR_COLOR, width=0.6, zorder=2)
    ax.errorbar(x, sub['comeback_rate_pct'],
                yerr=[sub['comeback_rate_pct'] - sub['ci_low'], sub['ci_high'] - sub['comeback_rate_pct']],
                fmt='none', ecolor=TEXT_COLOR, capsize=5, linewidth=1.5, zorder=3)
    ax.axhline(y=league_val, color=LEAGUE_COLOR, linewidth=2.5, linestyle='--', zorder=4,
               label=f'EuroLeague avg ({league_val:.1f}%)')

    for xi, (val, hi, n) in enumerate(zip(sub['comeback_rate_pct'], sub['ci_high'], sub['count'])):
        ax.text(xi, hi + 1.5, f'{val:.1f}%\n(n={n})', ha='center', va='bottom', fontweight='bold', color=TEXT_COLOR, fontsize=9,
                bbox=dict(facecolor=BG_COLOR, edgecolor='none', pad=1.5), zorder=5)

    ax.set_xticks(x)
    ax.set_xticklabels(ordered_labels, color=TEXT_COLOR, fontsize=9)
    ax.set_title(venue_label, color=TEXT_COLOR, fontsize=14)
    ax.set_ylabel('Comeback rate (%)', color=TEXT_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.set_ylim(0, 80)
    for spine in ax.spines.values():
        spine.set_color(BORDER_COLOR)

    legend = ax.legend(facecolor=BG_COLOR, edgecolor=BORDER_COLOR, loc='upper right', fontsize=9)
    plt.setp(legend.get_texts(), color=TEXT_COLOR)

fig.suptitle('Comeback rate after a 15+ point deficit, "hot arena" teams vs EuroLeague average\nEuroLeague seasons 2007-08 to 2025-26. Bars: 95% interval, n = games with a 15+ point deficit',
             color=TEXT_COLOR, fontsize=14, y=1.0)

plt.tight_layout()
plt.savefig(os.path.join(IMAGES_DIR, 'hot_arenas_comeback_rate.png'), dpi=150, facecolor=fig.get_facecolor(), pad_inches=0.3, bbox_inches='tight')
plt.show()

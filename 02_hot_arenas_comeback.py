import pandas as pd
import os
import matplotlib.pyplot as plt

# ============================================================
# 0. PATHS
# ============================================================

# Cartella dove si trova questo script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Adapt this line if your PC structure is different 
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

# ============================================================
# 1. LOAD DATA
# ============================================================

header = pd.read_csv(os.path.join(DATA_DIR, "euroleague_header.csv"))
pbp = pd.read_csv(os.path.join(DATA_DIR, "euroleague_play_by_play.csv"))

# ============================================================
# 2. LEAGUE-WIDE DEFICIT / COMEBACK CALCULATION
# (home & away perspective, computed for every game at once)
# ============================================================

pbp['quarter_order'] = pbp['quarter'].map(QUARTER_ORDER)
pbp = pbp.sort_values(['game_id', 'quarter_order', 'number_of_play'])

# Forward-fill scores within each game (non-scoring plays don't update points_a/points_b)
pbp[['points_a', 'points_b']] = pbp.groupby('game_id')[['points_a', 'points_b']].ffill()
pbp[['points_a', 'points_b']] = pbp[['points_a', 'points_b']].fillna(0)

pbp['deficit_home'] = pbp['points_a'] - pbp['points_b']
pbp['deficit_away'] = -pbp['deficit_home']

def analyze_game_full(group):
    """For a single game: find the worst deficit from both the home and away
    team's perspective, and whether each came back to tie or lead afterward."""
    group = group.reset_index(drop=True)

    idx_min_home = group['deficit_home'].idxmin()
    worst_home = group.loc[idx_min_home, 'deficit_home']
    comeback_home = (group.loc[idx_min_home:, 'deficit_home'] >= 0).any()

    idx_min_away = group['deficit_away'].idxmin()
    worst_away = group.loc[idx_min_away, 'deficit_away']
    comeback_away = (group.loc[idx_min_away:, 'deficit_away'] >= 0).any()

    return pd.Series({
        'worst_deficit_home': worst_home, 'comeback_home': comeback_home,
        'worst_deficit_away': worst_away, 'comeback_away': comeback_away
    })

print("Processing all EuroLeague games — this may take a couple of minutes...")
league_results = pbp.groupby('game_id').apply(analyze_game_full).reset_index()
print("Done.")

league_results = league_results.merge(
    header[['game_id', 'team_id_a', 'team_id_b']],
    on='game_id',
    how='left'
)

# ============================================================
# 3. RESHAPE TO LONG FORMAT (one row per team per game, with venue)
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
# 4. COMEBACK RATE, PER TEAM, PER VENUE
# ============================================================

big_deficit = team_long[team_long['worst_deficit'] <= DEFICIT_THRESHOLD].copy()

league_summary = big_deficit.groupby('venue')['comeback'].agg(['sum', 'count'])
league_summary['comeback_rate_pct'] = (league_summary['sum'] / league_summary['count'] * 100).round(1)

hot_teams_deficit = big_deficit[big_deficit['team_id'].isin(HOT_ARENA_TEAMS)]
hot_teams_summary = hot_teams_deficit.groupby(['team_id', 'venue'])['comeback'].agg(['sum', 'count']).reset_index()
hot_teams_summary['comeback_rate_pct'] = (hot_teams_summary['sum'] / hot_teams_summary['count'] * 100).round(1)

print("=== League average ===")
print(league_summary)
print("\n=== Hot arena teams ===")
print(hot_teams_summary)

# ============================================================
# 5. SEASON COVERAGE CHECK (for methodology notes: sample comparability across teams)
# ============================================================

print("\n=== Season coverage per team (games with a 15+ point deficit) ===")
for team in HOT_ARENA_TEAMS:
    team_games = big_deficit[big_deficit['team_id'] == team].merge(
        header[['game_id', 'season_code']], on='game_id', how='left'
    )
    seasons = sorted(team_games['season_code'].unique())
    print(f"{team}: {len(seasons)} seasons — {seasons}")

# ============================================================
# 6. PLOT: HOT ARENA TEAMS vs LEAGUE AVERAGE, HOME/AWAY
# ============================================================

BG_COLOR = '#0a1f3d'
BAR_COLOR = '#90EE90'
LEAGUE_COLOR = '#D35400'

hot_pivot = hot_teams_summary.pivot(index='team_id', columns='venue', values='comeback_rate_pct')
hot_pivot = hot_pivot.sort_values('Home', ascending=False)
ordered_labels = [TEAM_NAMES[t] for t in hot_pivot.index]

league_home = league_summary.loc['Home', 'comeback_rate_pct']
league_away = league_summary.loc['Away', 'comeback_rate_pct']

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.patch.set_facecolor(BG_COLOR)

panel_data = [('Home', hot_pivot['Home'], league_home), ('Away', hot_pivot['Away'], league_away)]

for ax, (venue_label, values, league_val) in zip(axes, panel_data):
    ax.set_facecolor(BG_COLOR)

    bars = ax.bar(ordered_labels, values, color=BAR_COLOR, width=0.6, zorder=2)
    ax.axhline(y=league_val, color=LEAGUE_COLOR, linewidth=2.5, linestyle='--', zorder=3, label=f'EuroLeague avg ({league_val}%)')

    ax.set_title(venue_label, color='white', fontsize=14)
    ax.set_ylabel('Comeback rate (%)', color='white')
    ax.tick_params(colors='white', rotation=20)
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.set_ylim(0, max(hot_pivot['Home'].max(), hot_pivot['Away'].max()) * 1.25)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1, f'{val}%', ha='center', fontweight='bold', color='white', fontsize=9)

    legend = ax.legend(facecolor=BG_COLOR, edgecolor='white', loc='upper right', fontsize=9)
    plt.setp(legend.get_texts(), color='white')

fig.suptitle('Comeback rate after a 15+ point deficit — "Hot arena" teams vs EuroLeague average', color='white', fontsize=15, y=1.02)

plt.tight_layout()
plt.savefig(os.path.join(IMAGES_DIR, 'hot_arenas_comeback_rate.png'), dpi=150, facecolor=fig.get_facecolor(), pad_inches=0.3, bbox_inches='tight')
plt.show()
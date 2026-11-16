# Hot arenas, big deficits: comeback rates of five EuroLeague teams

An analysis of comebacks after large deficits in EuroLeague play-by-play data (2007-08 to 2025-26). It compares five teams known for intense home crowds (Baskonia, Zalgiris, Panathinaikos, Partizan, Crvena Zvezda) against the league, home against away, with 95% intervals on every rate.

**Brief report:** [open the report](https://htmlpreview.github.io/?https://github.com/viare21/euroleague-hot-arenas/blob/main/hot_arenas_report.html)

## Results in brief

1. Every team comes back more often at home: league-wide the rate is 22.2% at home and 11.4% away, a gap of +10.8 points (95% interval +7.7 to +13.7). Each team has to be read against that baseline.
2. Only Partizan clearly stands out above it: 46.4% at home (interval 29.5 to 64.2, on 28 games), gap +35.8 (+15.5 to +56.2). Zalgiris stands out below: 10.3% at home (4.8 to 20.8), gap -1.9 (-11.5 to +8.4).
3. Panathinaikos (31.1%) and Baskonia (30.8%) are above the league average at home, but their intervals include it, and their gaps (+17.1 and +16.5) are compatible with the league gap. Crvena Zvezda (18.4%, gap +4.1) is indistinguishable from the league.

## Data

Source: [Euroleague & Eurocup Datasets](https://www.kaggle.com/datasets/babissamothrakis/euroleague-datasets) (Kaggle). 5,039 games, seasons `E2007` to `E2025`.

| File | Columns used |
|---|---|
| `euroleague_header.csv` | `game_id`, `season_code`, `team_id_a`, `team_id_b`, `score_a`, `score_b` |
| `euroleague_play_by_play.csv` | `game_id`, `quarter`, `number_of_play`, `points_a`, `points_b` |

Team A is the home team. The teams are identified by `team_id`: `BAS`, `ZAL`, `PAN`, `PAR`, `RED`.

All 19 seasons are used for the league average. The five teams have games in the dataset for these seasons:

| Team | Seasons in the dataset |
|---|---|
| Panathinaikos, Baskonia, Zalgiris | 19 (`E2007` to `E2025`) |
| Partizan | 11 (`E2007` to `E2013`, `E2022` to `E2025`) |
| Crvena Zvezda | 12 (`E2013` to `E2017`, `E2019` to `E2025`, none in `E2018`) |

## Project structure

| File | Role |
|---|---|
| `02_hot_arenas_comeback.py` | Main script: reconstructs the score, finds deficits and comebacks, computes rates and intervals, saves the chart |
| `images/` | Output chart (created by the script if missing) |
| `hot_arenas_report.html` | Brief report with the narrative and the findings |

The data files are not included in the repository. They are read from a `csv_euroleague` folder placed next to the project folder.

## How it works

The script is organised in numbered sections, run top to bottom.

1. **Load (1).** Header and play-by-play. Only five play-by-play columns are read, to keep memory use low.
2. **Score reconstruction (2).** Plays are sorted by game, period (`q1` to `q4`, then `extra_time`) and `number_of_play`. Scores are only filled on scoring plays, so they are forward-filled within each game. `deficit_home = points_a - points_b`.
3. **Data quality checks (2.1).** See the next section.
4. **Worst deficit and comeback (3).** For each game, from the home team's perspective the worst deficit is the minimum of `deficit_home`. From the away team's perspective it is the minimum of `-deficit_home`. A **comeback** means that, from the moment of that worst deficit onward, the team tied the score or led at least once before the final buzzer. It does not need to win. If the minimum is reached more than once, the first time is used.
5. **Long format (4).** One row per team per game, with venue.
6. **Rates and intervals (5).** Only team-games with a worst deficit of 15 points or more are kept. The comeback rate is comebacks over those games, by team and venue. The 95% interval is a Wilson interval. Each row is a different game for a given team and venue, so the rows are independent. The league average includes all teams, the five included.
7. **Home minus away gap (6).** For the league and each team: the difference between the home and the away rate, with a bootstrap interval (5,000 draws, home and away games resampled separately, fixed seed 42). Fisher's exact test on the home/away by comeback table is also printed for each team.
8. **Season coverage (7).** Seasons with at least one qualifying game, per team.
9. **Chart (8).** Home and away panels, with intervals and the league average.

### Design choices

- The worst deficit is searched over the whole game, not at a fixed moment such as the start of the fourth quarter. An earlier version on Baskonia alone defined a comeback as a win after trailing by 10 or more at the start of the fourth quarter, and it left only 1-2 qualifying games per team and venue.
- A comeback is defined as tying or leading, not winning, to keep the samples large enough to compare.
- Every team has a home advantage in comebacks, so reading a team's home rate only against the league's home rate mixes two things. The gap between home and away, compared with the league gap, takes this into account.

## Data quality checks

| Check | Result |
|---|---|
| Plays with an unrecognised quarter label | 0 |
| Games in the header and in the play-by-play | 5,039 and 5,039 |
| Reconstructed final score different from the official one | 34 games (0.7%) |
| Games where a team's score decreases at some point | 205 games (4.1%), including the 34 above |

The 205 games are kept in the main analysis. Without them the league rates are 22.0% at home and 11.7% away (22.2% and 11.4% with them), and the rates of the five teams change by at most 1.2 points. The conclusions do not depend on them.

## Outputs

![Comeback rate: hot arena teams vs EuroLeague average](images/hot_arenas_comeback_rate.png)

`images/hot_arenas_comeback_rate.png`: comeback rate after a 15+ point deficit, home and away, with 95% intervals and the number of qualifying games for each bar. The dashed line is the league average.

| Team | Home | Home 95% interval | Away | Away 95% interval | Home games | Away games |
|---|---|---|---|---|---|---|
| Partizan | 46.4% | 29.5 to 64.2 | 10.6% | 5.2 to 20.3 | 28 | 66 |
| Panathinaikos | 31.1% | 19.5 to 45.7 | 14.0% | 8.5 to 22.1 | 45 | 100 |
| Baskonia | 30.8% | 19.9 to 44.3 | 14.3% | 9.1 to 21.7 | 52 | 119 |
| Crvena Zvezda | 18.4% | 9.2 to 33.4 | 14.3% | 8.2 to 23.8 | 38 | 77 |
| Zalgiris | 10.3% | 4.8 to 20.8 | 12.2% | 7.1 to 20.2 | 58 | 98 |
| League | 22.2% | 19.7 to 24.9 | 11.4% | 10.1 to 13.0 | 978 | 1,864 |

Home minus away gap, in percentage points:

| Team | Gap | 95% interval | Fisher p |
|---|---|---|---|
| Partizan | +35.8 | +15.5 to +56.2 | < 0.001 |
| Panathinaikos | +17.1 | +1.8 to +32.4 | 0.022 |
| Baskonia | +16.5 | +3.0 to +30.8 | 0.019 |
| Crvena Zvezda | +4.1 | -10.3 to +18.6 | 0.59 |
| Zalgiris | -1.9 | -11.5 to +8.4 | 0.80 |
| League | +10.8 | +7.7 to +13.7 | |

The p-values come from five separate tests without correction for multiple testing.

## How to run

1. Download the dataset from Kaggle and place `euroleague_header.csv` and `euroleague_play_by_play.csv` in a folder named `csv_euroleague`, one level above this project's folder.
2. Install the requirements: `pip install pandas numpy matplotlib scipy statsmodels`
3. Run `02_hot_arenas_comeback.py`. It takes a few seconds to process all games.

In Spyder, press F5 to run the whole file. Running cell by cell (F9) also works: if `__file__` is not defined, the script falls back to the current working directory, so set it to the project folder first.

## Limitations and possible extensions

- The analysis is observational. A higher home comeback rate could reflect crowd energy, team quality, coaching or other factors that are not separated here.
- The samples are small, especially for Partizan (28 home games, 11 seasons in the dataset) and Crvena Zvezda (12 seasons). In the seasons missing for Partizan and Crvena Zvezda the dataset has no EuroLeague games for the team. According to public club records, they played other competitions in those years, mostly the EuroCup. Intervals are wide, and a team can rank first or last by chance.
- The five teams are compared with the league average, which includes them, and their results span many seasons with changing rosters and coaches.
- The list of "hot arena" teams was chosen by reputation, not by an independent metric. Attendance figures quoted in the report are approximate, come from external sources and are not computed in the script.
- The 15-point threshold and the tie-or-lead definition of a comeback are choices. The analysis could be extended by repeating it with 10 and 20 points, or by using wins instead of ties.
- It could also be extended by comparing all teams in the league, to see where the five rank among the 66 teams in the dataset, and by checking whether attendance explains home comeback rates across all teams, not only for five.

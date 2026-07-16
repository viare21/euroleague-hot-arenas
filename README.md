# Hot Arenas, Big Deficits: Does Crowd Intensity Predict Comebacks?

An extension of the Baskonia comeback-rate analysis to five EuroLeague teams commonly described as having some of the most intense home atmospheres in European basketball — testing whether that reputation is reflected in the data, and being explicit about where it isn't.

## Background

Five arenas are frequently cited among the loudest and most intense in EuroLeague basketball: the Fernando Buesa Arena (Baskonia), the Žalgirio Arena (Žalgiris), the OAKA / Telekom Center Athens (Panathinaikos), the Aleksandar Nikolić Hall / Stark Arena (Partizan), and the same Belgrade venue shared by Crvena Zvezda. This project asks a specific, testable question: **do these five teams recover from large deficits more often than the EuroLeague average, and more often at home than on the road?**

This project builds directly on an earlier single-team analysis of Baskonia's comeback rate, extending the same method to four additional teams and cross-checking the "hot arena" premise against independent attendance data.

## Data & Tools

- **Data source**: [Euroleague & Eurocup Datasets](https://www.kaggle.com/datasets/babissamothrakis/euroleague-datasets) (Kaggle) — play-by-play data (2.6M+ events) and game header/metadata
- **Tools**: Python, pandas, matplotlib
- **Scope**: Every EuroLeague game with play-by-play data available, filtered down to games where a team faced a deficit of 15+ points at some point

## Method

The metric is unchanged from the original Baskonia analysis:

1. For each team, in each game, find the single worst point deficit faced at any point in the game
2. Keep only games where that deficit was **15 points or worse**
3. Check whether, from that low point onward, the team tied the score or took the lead at any point before the final buzzer
4. Compare the resulting "comeback rate" — home vs away, team vs EuroLeague average

This is a *recovery* rate, not a *win* rate: a team that fought back to a tie and then lost still counts as a comeback here. This choice was made deliberately in the earlier Baskonia analysis, after an initial attempt using "win rate from a 10-point deficit at the start of the 4th quarter" produced samples too small to say anything reliable (as few as 1-2 qualifying wins per venue).

## Results: Comeback Rate by Team and Venue

![Comeback rate: hot arena teams vs EuroLeague average](images/hot_arenas_comeback_rate.png)

| Team | Home rate | Home games (15+ deficit) | Away rate | Away games (15+ deficit) | Home − League avg |
|---|---|---|---|---|---|
| **Partizan** | 46.4% | 28 | 10.6% | 66 | +24.2 |
| **Panathinaikos** | 31.1% | 45 | 14.0% | 100 | +8.9 |
| **Baskonia** | 30.8% | 52 | 14.3% | 119 | +8.6 |
| **Crvena Zvezda** | 18.4% | 38 | 14.3% | 77 | −3.8 |
| **Zalgiris** | 10.3% | 58 | 12.2% | 98 | −11.9 |
| *EuroLeague average* | *22.2%* | *978* | *11.4%* | *1,864* | — |

Three of the five teams (Partizan, Panathinaikos, Baskonia) sit clearly above the league average at home. Two (Crvena Zvezda, Zalgiris) sit at or below it. **Zalgiris is a particularly notable case**: it is the only one of the five teams where the home comeback rate (10.3%) is actually *lower* than its own away rate (12.2%) — the opposite of what the "loud home crowd" hypothesis would predict. This is worth flagging explicitly, since Zalgiris showed a clear, consistent home advantage in effort-driven box score stats (rebounds, blocks, second-chance points) in a separate analysis — a reminder that a team playing with more energy at home does not automatically translate into more successful comebacks. These appear to be related but distinct phenomena.

The away-game rates, by contrast, are far more compressed across all five teams (10.6%–14.3%), suggesting that whatever separates these teams shows up mainly in their home environment, not as a standing team trait.

## Is "Hot Arena" Just a Story? Checking Against Attendance Data

Before treating "hot arena" as a real category, it's worth checking it against something more concrete than reputation: actual attendance.

**Partizan and Crvena Zvezda** are, by a wide margin, the best-attended arenas in EuroLeague. In the 2023-24 season, Partizan averaged close to 20,000 fans per game in the 18,386-seat Stark Arena (a 98-99% fill rate), with Crvena Zvezda close behind at around 18,900 (94-95%) in the same shared venue. Both figures are independently confirmed by EuroLeague's own season recaps, not just reputation.

**Zalgiris** also fills its arena consistently, averaging around 14,900 fans in a 15,415-seat arena (roughly 96-97%) in 2023-24 — one of only two EuroLeague teams (alongside Maccabi Tel Aviv) regularly cited as filling over 95% of capacity.

**Panathinaikos** is a more volatile case. The team recorded EuroLeague's *lowest* attendance in 17 years during the 2022-23 season, then averaged 14,914 fans in 2023-24 (about 81% of the 18,300-seat OAKA), before EuroLeague reported a further 17.8% year-over-year increase in 2024-25, driven by the team's 2024 championship win. That would put 2024-25 attendance in the region of 17,000+, though this is an estimate derived from a reported percentage change rather than a directly published figure.

**Baskonia** stands out as the most surprising case here. Despite showing the second-strongest home comeback effect in this analysis (+8.6 points over the league average), its fill rate — around 70.5% of the Fernando Buesa Arena's 15,504 seats, per a 2023-24 season source — is unremarkable relative to the other teams here, closer to the EuroLeague-wide average (68%) than to Partizan or Zalgiris. If crowd size or fill rate were the main driver of the comeback effect, Baskonia's numbers wouldn't obviously predict it. This suggests that, if there's a real "atmosphere effect" for Baskonia, it may be more about crowd intensity than sheer size or occupancy — but this analysis doesn't have the data to test that distinction.

For context, **Fenerbahçe and Anadolu Efes** — both well-known clubs internationally, and both mentioned as possible "hot arena" candidates when this project was scoped — do not appear among EuroLeague's best-attended teams. Fenerbahçe averaged around 10,100-10,800 fans in a roughly 13,000-13,500 seat arena (around 80% full), and Anadolu Efes around 12,000 fans in a 16,000-seat arena (a fill rate in the neighborhood of 75%, calculated rather than directly sourced). Both are respectable numbers, but well short of the near-capacity crowds seen in Belgrade, Kaunas, or (more recently) Athens.

*All attendance figures above are drawn from EuroLeague season recaps and independent reporting (primarily 2023-24, with some 2024-25 context where available), and should be read as directional and approximate rather than precise, exact fill rates in particular are not consistently available across all teams and seasons, and some values here are estimates or calculations rather than directly published figures.*

## Sample Comparability Across Teams

Not all five teams have equally complete histories in this dataset, and this matters for how much weight to put on their numbers.

| Team | Seasons with a 15+ deficit game | Notes |
|---|---|---|
| Panathinaikos | 19 | Continuous EuroLeague history in the dataset |
| Baskonia | 19 | Continuous EuroLeague history in the dataset |
| Zalgiris | 19 | Continuous EuroLeague history in the dataset |
| Crvena Zvezda | 12 | EuroLeague debut in 2014-15; competed in EuroCup before that |
| Partizan | 11 | Absent from EuroLeague 2014-15 through 2021-22 due to licensing/financial issues; competed in EuroCup during that period; returned in 2022-23 |

Partizan's standout home comeback rate (46.4%) is based on the smallest sample here (28 home games meeting the threshold), concentrated mostly in recent seasons (2022-23 onward, plus a handful from 2007-2013). This doesn't invalidate the finding, but it does mean it reflects a narrower, more recent slice of EuroLeague basketball than the figures for Panathinaikos, Baskonia, or Zalgiris. Interestingly, the arena itself (opened in 2004, renamed from Belgrade Arena → Kombank Arena → Stark Arena over the years) has been in continuous use for Partizan's EuroLeague home games across both eras — so the gap in the data reflects a competition-eligibility gap, not a change of venue.

## Blind Spots and Further Research Needed

This analysis has several limitations worth stating plainly:

- **No formal significance testing was run team-by-team here** (unlike the dedicated Baskonia analysis, where neither a two-proportion z-test nor a Fisher's exact test reached conventional significance for the home/away gap). With similarly modest sample sizes for some of these teams — especially Partizan (28 home games) and Crvena Zvezda (38) — the same caution almost certainly applies: an interesting gap in the data is not the same as a statistically confirmed effect.
- **This is correlational, not causal.** A higher comeback rate at home could reflect crowd energy, but it could equally reflect team quality, coaching, opponent scheduling quirks, travel fatigue for visiting teams, or simply that better teams tend to also have bigger, louder fan bases — the analysis cannot separate these explanations.
- **Attendance figures used here come from a single recent season (2023-24) or nearby years**, while the comeback-rate analysis spans up to 19 seasons per team. Crowd size and atmosphere may have changed substantially over that period (Partizan's and Crvena Zvezda's attendance, for example, grew sharply after their EuroLeague returns), so the two datasets aren't perfectly time-matched.
- **"Loud arena" as a category was defined subjectively**, based on common reputation, not a systematic ranking — a more rigorous version of this project would define "loud" using a consistent, independent metric (e.g. decibel data, if it existed, or a longer attendance time series) rather than starting from anecdote.
- **The 15-point deficit threshold and the "tied or ahead" comeback definition are one reasonable choice among several.** Different thresholds might shift which teams look most affected by home court, and this hasn't been tested for robustness across teams the way it partially was for Baskonia alone.

None of this means the pattern isn't real — for Partizan and Baskonia in particular, the gap is large and directionally consistent with the "hot arena" reputation. But it should be read as a data-informed starting point for a stronger, more controlled analysis (larger samples, formal significance testing per team, and independent measures of crowd intensity), not as a settled conclusion.

## Takeaways

- **The "hot arena" premise is only partially supported by the data.** Three of five reputationally "loud" teams (Partizan, Panathinaikos, Baskonia) show a clear home advantage in comeback rate; two (Crvena Zvezda, Zalgiris) do not.
- **Partizan and Crvena Zvezda's reputations are backed by genuinely exceptional, independently verified attendance figures** — the best-attended arenas in EuroLeague by a wide margin.
- **Baskonia's strong comeback numbers are not obviously explained by crowd size or fill rate**, which are closer to league-average — an interesting open question rather than a resolved one.
- **Zalgiris shows the opposite pattern** to what the hypothesis predicts, despite showing a clear home advantage in effort-based box score stats in a related analysis — a useful reminder that different "home advantage" metrics don't always move together.
- **Sample sizes vary meaningfully across teams**, driven by real, well-documented differences in EuroLeague participation history (not missing data) — Partizan and Crvena Zvezda's numbers should be read with that context in mind.

## How to Reproduce

1. Download the [Euroleague & Eurocup Datasets](https://www.kaggle.com/datasets/babissamothrakis/euroleague-datasets) from Kaggle
2. Place `euroleague_header.csv` and `euroleague_play_by_play.csv` in a `csv_euroleague` folder
3. Run the analysis script (requires `pandas`, `matplotlib`)

Note: processing the full league-wide play-by-play file (2.6M+ rows) takes a couple of minutes to run.

## About

This project combines a background in basketball coaching (8 years, youth and regional level) with data analysis. See also:
- [Olympiacos 2025-26: A Shot Data Analysis](https://github.com/viare21/euroleague-shot-analysis)
- [Zalgiris Kaunas: The Home Court Effort Effect](https://github.com/viare21/zalgiris-home-effort) *(update link once repository is created)*
- [Baskonia: Debunking (and Confirming) the Comeback Myth](https://github.com/viare21/baskonia-comeback-analysis) *(update link once repository is created)*

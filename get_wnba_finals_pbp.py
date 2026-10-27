"""
Download the play-by-play of the 2026 WNBA Finals games
(Atlanta Dream vs Golden State Valkyries) from the official WNBA/NBA stats API.

How to run (Mac Terminal):
    pip3 install nba_api pandas
    python3 get_wnba_finals_pbp.py

Output: one CSV per Finals game, in a folder "wnba_finals_pbp" next to this script,
plus "games.csv" with the list of games found.
"""
import time
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv3

WNBA = "10"                 # league id of the WNBA in the stats API
SEASON = "2026"
TEAMS = {"ATL", "GSV"}      # Atlanta Dream, Golden State Valkyries
FINALS_START = "2026-10-15"  # Finals Game 1 was on 2026-10-17

out = Path(__file__).with_name("wnba_finals_pbp")
out.mkdir(exist_ok=True)

print("Looking for the Finals games...")
finder = leaguegamefinder.LeagueGameFinder(
    league_id_nullable=WNBA,
    season_nullable=SEASON,
    season_type_nullable="Playoffs",
    timeout=60,
)
games = finder.get_data_frames()[0]
games = games[games["TEAM_ABBREVIATION"].isin(TEAMS)]
games = games[games["GAME_DATE"] >= FINALS_START]
# Each game appears twice (one row per team); keep the matchups ATL vs GSV only.
games = games[games["MATCHUP"].str.contains("ATL") & games["MATCHUP"].str.contains("GSV")]
games = games.drop_duplicates("GAME_ID").sort_values("GAME_DATE")

if games.empty:
    raise SystemExit("No Finals games found. Send me the full output of this window.")

games[["GAME_ID", "GAME_DATE", "MATCHUP"]].to_csv(out / "games.csv", index=False)
print(games[["GAME_ID", "GAME_DATE", "MATCHUP"]].to_string(index=False))

for n, row in enumerate(games.itertuples(), start=1):
    print(f"Downloading Game {n} ({row.GAME_DATE}, id {row.GAME_ID})...")
    pbp = playbyplayv3.PlayByPlayV3(game_id=row.GAME_ID, timeout=60).get_data_frames()[0]
    file = out / f"finals_game{n}_{row.GAME_DATE}_{row.GAME_ID}.csv"
    pbp.to_csv(file, index=False)
    print(f"  {len(pbp)} events saved to {file.name}")
    time.sleep(1.5)  # be polite to the API

print(f"\nDone. Send me the CSV files in: {out}")

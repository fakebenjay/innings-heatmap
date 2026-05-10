import statsapi
from IPython import embed
import pandas as pd
import numpy as np


def safe_integer(number):
    try:
        return int(number)
    except Exception:
        return ""


def verify(line):
    for inning in line:
        if inning > 9:
            return True

    return False


def final_scoring_play(pbp):
    plays = []
    for index, play in enumerate(pbp):
        if index + 1 < len(pbp):
            this_score = pbp[index]["half"] + str(pbp[index]["inning"])
            next_score = pbp[index + 1]["half"] + str(pbp[index + 1]["inning"])
            if this_score != next_score:
                plays.append(play)

    plays.append(pbp[len(pbp) - 1])
    return plays


def tally_runs(pbp, status):
    line = [0] * 33
    plays = list(filter(lambda x: x["half"] == status, pbp))
    key = "away_score" if status == "bottom" else "home_score"
    running_score = plays[0][key] if len(plays) > 0 else 0
    line[plays[0]["inning"] - 1] = plays[0][key]

    for index, play in enumerate(plays):
        if index != 0:
            line[play["inning"] - 1] = plays[index][key] - running_score
            running_score = plays[index][key]

    return line


df = pd.read_excel("innings_blank.xlsx", index_col=0)

games_2026 = statsapi.schedule(start_date="01/01/2026", end_date="12/31/2026")
done_regular_games_2026 = list(
    filter(lambda x: x["game_type"] == "R" and x["status"] == "Final", games_2026)
)


for g in done_regular_games_2026:
    linescore = statsapi.linescore(g["game_id"])
    linescore_list = linescore.split("\n")

    away_line_raw = list(map(lambda x: safe_integer(x), linescore_list[2].split(" ")))
    home_line_raw = list(map(lambda x: safe_integer(x), linescore_list[1].split(" ")))

    away_name = g["away_name"]
    home_name = g["home_name"]

    away_id = g["away_id"]
    home_id = g["home_id"]

    away = list(
        map(
            lambda x: int(x),
            list(filter(lambda x: x != "", away_line_raw)),
        )
    )
    home = list(
        map(
            lambda x: int(x),
            list(filter(lambda x: x != "", home_line_raw)),
        )
    )

    away_innings = away[:-3] if g["inning_state"] == "Bottom" else home[:-4]
    home_innings = home[:-3]

    if verify(away_innings) or verify(home_innings):
        play_by_play = statsapi.game_scoring_play_data(g["game_id"])

        pbp_filter_1 = list(
            map(
                lambda x: {
                    "away_score": x["result"]["awayScore"],
                    "home_score": x["result"]["homeScore"],
                    "half": x["about"]["halfInning"],
                    "inning": x["about"]["inning"],
                },
                play_by_play["plays"],
            )
        )

        pbp = final_scoring_play(pbp_filter_1)

        away_innings = (
            tally_runs(pbp, "bottom")[: g["current_inning"]]
            if g["inning_state"] == "Bottom"
            else tally_runs(pbp, "bottom")[: g["current_inning"] - 1]
        )
        home_innings = tally_runs(pbp, "top")[: g["current_inning"]]

    away_extras = away_innings[9:]
    home_extras = home_innings[9:]
    away_extras_runs = sum(away_extras) if len(away_extras) > 0 else float("nan")
    home_extras_runs = sum(home_extras) if len(home_extras) > 0 else float("nan")

    if g["current_inning"] > 9:
        away_extras_played = g["current_inning"] - 9
        home_extras_played = (
            g["current_inning"] - 9
            if g["inning_state"] == "Bottom"
            else g["current_inning"] - 10
        )
    else:
        away_extras_played = 0
        home_extras_played = 0

    away_score = g["home_score"]
    home_score = g["away_score"]

    away_iloc = df.loc[(df.index == away_id) & (df["status"] == "Away")].iloc[0]
    home_iloc = df.loc[(df.index == home_id) & (df["status"] == "Home")].iloc[0]

    away_total_iloc = df.loc[(df.index == away_id) & (df["status"] == "Total")].iloc[0]
    home_total_iloc = df.loc[(df.index == home_id) & (df["status"] == "Total")].iloc[0]

    for index, runs in enumerate(away_innings):
        away_iloc.loc[index + 1] = (
            away_iloc.loc[index + 1] + runs
            if pd.notna(away_iloc.loc[index + 1])
            else runs
        )
        away_iloc.loc["runs_adj"] = (
            away_iloc.loc["runs_adj"] + (runs * (index + 1))
            if pd.notna(away_iloc.loc["runs_adj"])
            else runs * (index + 1)
        )
        away_iloc.loc[str(index + 1) + "p"] = (
            away_iloc.loc[str(index + 1) + "p"] + 1
            if pd.notna(away_iloc.loc[str(index + 1) + "p"])
            else 1
        )
        away_total_iloc.loc[index + 1] = (
            away_total_iloc.loc[index + 1] + runs
            if pd.notna(away_total_iloc.loc[index + 1])
            else runs
        )
        away_total_iloc.loc["runs_adj"] = (
            away_total_iloc.loc["runs_adj"] + (runs * (index + 1))
            if pd.notna(away_total_iloc.loc["runs_adj"])
            else runs * (index + 1)
        )
        away_total_iloc.loc[str(index + 1) + "p"] = (
            away_total_iloc.loc[str(index + 1) + "p"] + 1
            if pd.notna(away_total_iloc.loc[str(index + 1) + "p"])
            else 1
        )

    for index, runs in enumerate(home_innings):
        home_iloc.loc[index + 1] = (
            home_iloc.loc[index + 1] + runs
            if pd.notna(home_iloc.loc[index + 1])
            else runs
        )
        home_iloc.loc["runs_adj"] = (
            home_iloc.loc["runs_adj"] + (runs * (index + 1))
            if pd.notna(home_iloc.loc["runs_adj"])
            else runs * (index + 1)
        )
        home_iloc.loc[str(index + 1) + "p"] = (
            home_iloc.loc[str(index + 1) + "p"] + 1
            if pd.notna(home_iloc.loc[str(index + 1) + "p"])
            else 1
        )
        home_total_iloc.loc[index + 1] = (
            home_total_iloc.loc[index + 1] + runs
            if pd.notna(home_total_iloc.loc[index + 1])
            else runs
        )
        home_total_iloc.loc["runs_adj"] = (
            home_total_iloc.loc["runs_adj"] + (runs * (index + 1))
            if pd.notna(home_total_iloc.loc["runs_adj"])
            else runs * (index + 1)
        )
        home_total_iloc.loc[str(index + 1) + "p"] = (
            home_total_iloc.loc[str(index + 1) + "p"] + 1
            if pd.notna(home_total_iloc.loc[str(index + 1) + "p"])
            else 1
        )

    away_iloc.loc["runs"] = (
        away_iloc.loc["runs"] + away_score
        if pd.notna(away_iloc.loc["runs"])
        else away_score
    )
    away_total_iloc.loc["runs"] = (
        away_total_iloc.loc["runs"] + away_score
        if pd.notna(away_total_iloc.loc["runs"])
        else away_score
    )

    home_iloc.loc["runs"] = (
        home_iloc.loc["runs"] + home_score
        if pd.notna(home_iloc.loc["runs"])
        else home_score
    )
    home_total_iloc.loc["runs"] = (
        home_total_iloc.loc["runs"] + home_score
        if pd.notna(home_total_iloc.loc["runs"])
        else home_score
    )

    away_iloc.loc["w"] = (
        away_iloc.loc["w"] + 1
        if g["away_name"] == g["winning_team"]
        else away_iloc.loc["w"]
    )
    away_total_iloc.loc["w"] = (
        away_total_iloc.loc["w"] + 1
        if g["away_name"] == g["winning_team"]
        else away_total_iloc.loc["w"]
    )

    home_iloc.loc["w"] = (
        home_iloc.loc["w"] + 1
        if g["home_name"] == g["winning_team"]
        else home_iloc.loc["w"]
    )
    home_total_iloc.loc["w"] = (
        home_total_iloc.loc["w"] + 1
        if g["home_name"] == g["winning_team"]
        else home_total_iloc.loc["w"]
    )

    away_iloc.loc["l"] = (
        away_iloc.loc["l"] + 1
        if g["away_name"] == g["losing_team"]
        else away_iloc.loc["l"]
    )
    away_total_iloc.loc["l"] = (
        away_total_iloc.loc["l"] + 1
        if g["away_name"] == g["losing_team"]
        else away_total_iloc.loc["l"]
    )

    home_iloc.loc["l"] = (
        home_iloc.loc["l"] + 1
        if g["home_name"] == g["losing_team"]
        else home_iloc.loc["l"]
    )
    home_total_iloc.loc["l"] = (
        home_total_iloc.loc["l"] + 1
        if g["home_name"] == g["losing_team"]
        else home_total_iloc.loc["l"]
    )

    if pd.notna(away_extras_runs):
        away_iloc.loc["x"] = (
            away_iloc.loc["x"] + away_extras_runs
            if pd.notna(away_iloc.loc["x"])
            else away_extras_runs
        )
        away_total_iloc.loc["x"] = (
            away_total_iloc.loc["x"] + away_extras_runs
            if pd.notna(away_total_iloc.loc["x"])
            else away_extras_runs
        )

    if pd.notna(home_extras_runs):
        home_iloc.loc["x"] = (
            home_iloc.loc["x"] + home_extras_runs
            if pd.notna(home_iloc.loc["x"])
            else home_extras_runs
        )
        home_total_iloc.loc["x"] = (
            home_total_iloc.loc["x"] + home_extras_runs
            if pd.notna(home_total_iloc.loc["x"])
            else home_extras_runs
        )

    away_iloc.loc["xp"] = (
        away_iloc.loc["xp"] + away_extras_played
        if pd.notna(away_iloc.loc["xp"])
        else away_extras_played
    )
    away_total_iloc.loc["xp"] = (
        away_total_iloc.loc["xp"] + away_extras_played
        if pd.notna(away_total_iloc.loc["xp"])
        else away_extras_played
    )
    home_iloc.loc["xp"] = (
        home_iloc.loc["xp"] + home_extras_played
        if pd.notna(home_iloc.loc["xp"])
        else home_extras_played
    )
    home_total_iloc.loc["xp"] = (
        home_total_iloc.loc["xp"] + home_extras_played
        if pd.notna(home_total_iloc.loc["xp"])
        else home_extras_played
    )

    df.loc[(df.index == away_id) & (df["status"] == "Away")] = list(away_iloc)
    df.loc[(df.index == home_id) & (df["status"] == "Home")] = list(home_iloc)

    df.loc[(df.index == away_id) & (df["status"] == "Total")] = list(away_total_iloc)
    df.loc[(df.index == home_id) & (df["status"] == "Total")] = list(home_total_iloc)

    print(g["summary"])

df["center_of_gravity"] = df["runs_adj"] / df["runs"]

for inning in list(range(1, 33)):
    df[str(inning) + "avg"] = df[inning] / df[str(inning) + "p"]

df["xavg"] = df["x"] / df["xp"]

# df["html"] = df.apply(
#     lambda x: f"<div style='display:flex;'><span style='flex:1;aspect-ratio:1 / 1; min-width:0;'><img alt='{x['team_name']} cap logo' style='width:100%;' src='https://github.com/fakebenjay/innings-heatmap/blob/master/logos/{x['code']}.png'/></span><span style='background-color:{str(x['hex_bg'])};color:{str(x['hex_text'])};{"-webkit-text-stroke:0.5px " if pd.notna(x['hex_ol']) else ''}{str(x['hex_ol'] + ";") if pd.notna(x['hex_ol']) else ''}flex:1;aspect-ratio:1 / 3; min-width:0;font-size:10px;'>{x['team_name']}<br/><small>{str(x['runs'])} runs in {str(x['1p'])} games</small></span></div>",
#     axis=1,
# )

df.to_csv("defense.csv")
df.to_excel("defense.xlsx")

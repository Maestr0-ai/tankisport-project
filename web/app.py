import json
from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__)

# ⬇️ ВАЖНО: файл лежит на уровень выше папки web
DATA_FILE = Path(__file__).resolve().parent.parent / "team_data.json"


def load_data():
    if not DATA_FILE.exists():
        print("❌ team_data.json NOT FOUND:", DATA_FILE)
        return {}, {}, {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    teams = data.get("team_states", {})
    tournament = data.get("tournament_states", {}).get("842", {})
    schedule = tournament.get("schedule", {})

    return teams, tournament, schedule


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/schedule")
def schedule():
    teams, tournament, schedule_data = load_data()

    matches = []

    for round_num, round_matches in schedule_data.items():
        if not isinstance(round_matches, list):
            continue

        for match in round_matches:
            teams_data = match.get("teams", {})
            team1_id = str(teams_data.get("team1_id", ""))
            team2_id = str(teams_data.get("team2_id", ""))

            team1_name = teams.get(team1_id, {}).get("name", f"Team {team1_id}")
            team2_name = teams.get(team2_id, {}).get("name", f"Team {team2_id}")

            matches.append({
                "round": round_num,
                "time": match.get("time", ""),
                "detail": match.get("detail", ""),
                "team1": team1_name,
                "team2": team2_name,
            })

    return render_template("schedule.html", matches=matches)

@app.route("/results")
def results():
    teams, tournament, _ = load_data()
    results = tournament.get("match_results", {})

    rounds = []
    for round_num, matches in results.items():
        rounds.append({
            "round": round_num,
            "matches": matches
        })

    return render_template("results.html", rounds=rounds)


@app.route("/teams")
def teams():
    teams, _, _ = load_data()
    return render_template("teams.html", teams=teams)


@app.route("/stats")
def stats():
    _, tournament, _ = load_data()
    return render_template("stats.html", tournament=tournament)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, render_template
import json
from datetime import datetime

app = Flask(__name__)

# ---------- helpers ----------

def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return default if default is not None else {}

def format_time(ts):
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d.%m %H:%M")
    except:
        return ts

# ---------- routes ----------

@app.route("/")
def index():
    data = load_json("../team_data.json")
    tournaments = data.get("tournament_states", {})
    tournament = next(iter(tournaments.values()), {})
    results = tournament.get("match_results", {})
    return render_template("index.html", results=results)


@app.route("/schedule")
def schedule():
    data = load_json("../team_data.json")

    team_states = data.get("team_states", {})
    tournaments = data.get("tournament_states", {})
    tournament = next(iter(tournaments.values()), {})

    raw_schedule = tournament.get("schedule", [])
    matches = []

    for match in raw_schedule:
        team1_id = str(match["teams"]["team1_id"])
        team2_id = str(match["teams"]["team2_id"])

        team1 = team_states.get(team1_id, {}).get("name", "Unknown")
        team2 = team_states.get(team2_id, {}).get("name", "Unknown")

        matches.append({
            "match_id": match.get("match_id"),
            "time": format_time(match.get("time")),
            "team1": team1,
            "team2": team2,
            "detail": match.get("detail", "")
        })

    return render_template("schedule.html", matches=matches)


@app.route("/teams")
def teams():
    data = load_json("../team_data.json")
    teams = data.get("team_states", {})
    return render_template("teams.html", teams=teams)


@app.route("/stats")
def stats():
    data = load_json("../team_data.json")
    teams = data.get("team_states", {})
    return render_template("stats.html", teams=teams)


# ---------- run ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)

from flask import Flask, render_template
import requests
from datetime import datetime
import os

app = Flask(__name__)

# ================== НАСТРОЙКИ ==================
TOURNAMENT_API = "https://tankisport.com/api/tournaments/show/842"
TIMEOUT = 20


# ================== API ==================
def fetch_tournament():
    r = requests.get(TOURNAMENT_API, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def parse_matches(data):
    matches = []

    for stage in data.get("stages", []):
        round_name = stage.get("name", "Unknown")

        for m in stage.get("matches", []):
            start = datetime.fromisoformat(
                m["start_time"].replace("Z", "+00:00")
            )

            matches.append({
                "round": round_name,
                "team1": m["team1"]["name"],
                "team2": m["team2"]["name"],
                "start_time": start,
                "time_iso": start.isoformat(),
                "time_display": start.strftime("%d.%m.%Y %H:%M"),
                "score1": m.get("score1"),
                "score2": m.get("score2"),
                "status": m.get("status")  # scheduled | live | finished
            })

    return matches


def parse_teams(data):
    teams = {}

    for stage in data.get("stages", []):
        for m in stage.get("matches", []):
            t1 = m["team1"]["name"]
            t2 = m["team2"]["name"]

            teams.setdefault(t1, {"played": 0, "wins": 0, "losses": 0})
            teams.setdefault(t2, {"played": 0, "wins": 0, "losses": 0})

            if m.get("status") == "finished":
                teams[t1]["played"] += 1
                teams[t2]["played"] += 1

                if m["score1"] > m["score2"]:
                    teams[t1]["wins"] += 1
                    teams[t2]["losses"] += 1
                else:
                    teams[t2]["wins"] += 1
                    teams[t1]["losses"] += 1

    return teams


# ================== РОУТЫ ==================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/schedule")
def schedule():
    data = fetch_tournament()
    matches = parse_matches(data)

    active = [
        m for m in matches
        if m["status"] in ("scheduled", "live")
    ]

    active.sort(key=lambda x: x["start_time"])
    return render_template("schedule.html", matches=active)


@app.route("/results")
def results():
    data = fetch_tournament()
    matches = parse_matches(data)

    results_by_round = {}
    for m in matches:
        if m["status"] == "finished":
            results_by_round.setdefault(m["round"], []).append(m)

    return render_template("results.html", results_by_round=results_by_round)


@app.route("/teams")
def teams():
    data = fetch_tournament()
    teams = parse_teams(data)

    return render_template("teams.html", teams=teams)


@app.route("/stats")
def stats():
    data = fetch_tournament()
    matches = parse_matches(data)

    total = len(matches)
    finished = len([m for m in matches if m["status"] == "finished"])
    live = len([m for m in matches if m["status"] == "live"])

    return render_template(
        "stats.html",
        total=total,
        finished=finished,
        live=live
    )


# ================== RENDER ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

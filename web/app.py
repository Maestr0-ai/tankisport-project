from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

TOURNAMENT_ID = 842
API_TOURNAMENT = f"https://tankisport.com/api/tournaments/show/{TOURNAMENT_ID}"


def get_tournament_data():
    try:
        r = requests.get(API_TOURNAMENT, timeout=10)
        r.raise_for_status()
        return r.json()["data"]
    except Exception as e:
        print("API ERROR:", e)
        return None


def parse_matches():
    data = get_tournament_data()
    if not data:
        return [], []

    matches_raw = data.get("matches", [])
    schedule = []
    results = []

    now = datetime.now()

    for m in matches_raw:
        date = datetime.strptime(m["date"], "%Y-%m-%d %H:%M:%S")

        match = {
            "id": m["id"],
            "team1": m["team1"]["name"],
            "team2": m["team2"]["name"],
            "team1_id": m["team1"]["id"],
            "team2_id": m["team2"]["id"],
            "time": date,
            "time_iso": date.isoformat(),
            "time_display": date.strftime("%d.%m.%Y %H:%M"),
            "score1": m["result1"],
            "score2": m["result2"],
            "round": m.get("connection", {}).get("stage", 1),
            "scores": m.get("scores", []),
            "winner": m.get("winner")
        }

        # --- СТАТУС МАТЧА ---
        if match["winner"]:
            match["state"] = "finished"
            results.append(match)

        elif match["scores"]:
            match["state"] = "live"
            schedule.append(match)

        else:
            match["state"] = "upcoming"
            schedule.append(match)

    return schedule, results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/schedule")
def schedule():
    schedule, _ = parse_matches()
    return render_template("schedule.html", matches=schedule)


@app.route("/results")
def results():
    _, results = parse_matches()

    results_by_round = {}
    for m in results:
        r = m["round"]
        results_by_round.setdefault(r, []).append(m)

    return render_template("results.html", results_by_round=results_by_round)


@app.route("/stats")
def stats():
    schedule, results = parse_matches()

    stats = {
        "total": len(schedule) + len(results),
        "finished": len(results),
        "live": len([m for m in schedule if m["state"] == "live"]),
        "upcoming": len([m for m in schedule if m["state"] == "upcoming"]),
    }

    return render_template("stats.html", stats=stats)


@app.route("/teams")
def teams():
    data = get_tournament_data()
    teams = {}

    for m in data.get("matches", []):
        teams[m["team1"]["id"]] = m["team1"]
        teams[m["team2"]["id"]] = m["team2"]

    return render_template("teams.html", teams=teams.values())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

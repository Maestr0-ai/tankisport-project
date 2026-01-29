from flask import Flask, render_template
import requests
from datetime import datetime, timezone

app = Flask(__name__)

TOURNAMENT_ID = 842
API_TOURNAMENT = f"https://tankisport.com/api/tournaments/show/{TOURNAMENT_ID}"

def fetch_tournament():
    try:
        r = requests.get(API_TOURNAMENT, timeout=15)
        r.raise_for_status()
        return r.json()["data"]
    except Exception as e:
        print("API ERROR:", e)
        return None

def parse_datetime(dt):
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/schedule")
def schedule():
    tournament = fetch_tournament()
    if not tournament:
        return render_template("schedule.html", matches=[])

    now = datetime.now(timezone.utc)
    matches = []

    for m in tournament.get("matches", []):
        start = parse_datetime(m["date"])

        if m["status"] in (0, 1):  # ожидается или LIVE
            matches.append({
                "team1": m["team1"]["name"],
                "team2": m["team2"]["name"],
                "time_iso": start.isoformat(),
                "time_display": start.strftime("%d.%m.%Y %H:%M"),
                "status": m["status"]
            })

    matches.sort(key=lambda x: x["time_iso"])
    return render_template("schedule.html", matches=matches)

@app.route("/results")
def results():
    tournament = fetch_tournament()
    results_by_round = {}

    if not tournament:
        return render_template("results.html", results_by_round={})

    for m in tournament.get("matches", []):
        if m["status"] != 2:
            continue  # только завершённые

        stage = m["connection"]["stage"]
        results_by_round.setdefault(stage, [])

        results_by_round[stage].append({
            "team1": m["team1"]["name"],
            "team2": m["team2"]["name"],
            "score1": m["result1"],
            "score2": m["result2"]
        })

    return render_template("results.html", results_by_round=results_by_round)

@app.route("/teams")
def teams():
    tournament = fetch_tournament()
    teams = {}

    if tournament:
        for m in tournament.get("matches", []):
            teams[m["team1"]["id"]] = m["team1"]
            teams[m["team2"]["id"]] = m["team2"]

    return render_template("teams.html", teams=list(teams.values()))

@app.route("/stats")
def stats():
    tournament = fetch_tournament()
    total = live = finished = upcoming = 0

    if tournament:
        for m in tournament.get("matches", []):
            total += 1
            if m["status"] == 0:
                upcoming += 1
            elif m["status"] == 1:
                live += 1
            elif m["status"] == 2:
                finished += 1

    return render_template(
        "stats.html",
        total=total,
        live=live,
        finished=finished,
        upcoming=upcoming
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

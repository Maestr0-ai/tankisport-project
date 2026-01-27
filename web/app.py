from flask import Flask, render_template
import requests
from datetime import datetime, timezone

app = Flask(__name__)

TOURNAMENT_API = "https://tankisport.com/api/tournaments/show/842"


def fetch_tournament():
    r = requests.get(TOURNAMENT_API, timeout=20)
    r.raise_for_status()
    return r.json()


def parse_matches(data):
    matches = []

    for stage in data.get("stages", []):
        round_name = stage.get("name", "Unknown")

        for match in stage.get("matches", []):
            team1 = match["team1"]["name"]
            team2 = match["team2"]["name"]

            start_time = datetime.fromisoformat(
                match["start_time"].replace("Z", "+00:00")
            )

            score1 = match.get("score1")
            score2 = match.get("score2")

            status = match.get("status")  # scheduled | live | finished

            matches.append({
                "round": round_name,
                "team1": team1,
                "team2": team2,
                "start_time": start_time,
                "start_iso": start_time.isoformat(),
                "start_display": start_time.strftime("%d.%m.%Y %H:%M"),
                "score1": score1,
                "score2": score2,
                "status": status,
            })

    return matches


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/matches")
def matches():
    data = fetch_tournament()
    all_matches = parse_matches(data)

    now = datetime.now(timezone.utc)

    upcoming_and_live = [
        m for m in all_matches
        if m["status"] in ("scheduled", "live")
    ]

    upcoming_and_live.sort(key=lambda x: x["start_time"])

    return render_template(
        "schedule.html",
        matches=upcoming_and_live,
        now_iso=now.isoformat()
    )


@app.route("/results")
def results():
    data = fetch_tournament()
    all_matches = parse_matches(data)

    results_by_round = {}

    for m in all_matches:
        if m["status"] == "finished":
            results_by_round.setdefault(m["round"], []).append(m)

    return render_template(
        "results.html",
        results_by_round=results_by_round
    )


if __name__ == "__main__":
    app.run(debug=True)

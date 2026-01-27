from flask import Flask, render_template
import requests
from datetime import datetime, timezone
import os

app = Flask(__name__)

# ===== НАСТРОЙКИ =====
TOURNAMENT_API = "https://tankisport.com/api/tournaments/show/842"
REQUEST_TIMEOUT = 20


# ===== ЗАГРУЗКА ДАННЫХ =====
def fetch_tournament():
    response = requests.get(TOURNAMENT_API, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


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

            status = match.get("status")  # scheduled | live | finished

            matches.append({
                "round": round_name,
                "team1": team1,
                "team2": team2,
                "start_time": start_time,
                "time_iso": start_time.isoformat(),
                "time_display": start_time.strftime("%d.%m.%Y %H:%M"),
                "score1": match.get("score1"),
                "score2": match.get("score2"),
                "status": status,
            })

    return matches


# ===== РОУТЫ =====
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/matches")
def matches():
    data = fetch_tournament()
    all_matches = parse_matches(data)

    # Показываем ТОЛЬКО запланированные и LIVE
    active_matches = [
        m for m in all_matches
        if m["status"] in ("scheduled", "live")
    ]

    active_matches.sort(key=lambda x: x["start_time"])

    return render_template(
        "schedule.html",
        matches=active_matches,
        now_iso=datetime.now(timezone.utc).isoformat()
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


# ===== ЗАПУСК ДЛЯ RENDER =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

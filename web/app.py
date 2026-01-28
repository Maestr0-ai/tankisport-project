from flask import Flask, render_template
import requests
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# ===== НАСТРОЙКИ =====
TOURNAMENT_ID = 842

API_TOURNAMENT = f"https://tankisport.com/api/tournaments/show/{TOURNAMENT_ID}"
API_MATCHES = f"https://tankisport.com/api/matches?tournament={TOURNAMENT_ID}"


# ===== ВСПОМОГАТЕЛЬНЫЕ =====
def fetch_json(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("API ERROR:", e)
        return None


def parse_datetime(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


# ===== ГЛАВНАЯ =====
@app.route("/")
def index():
    return render_template("index.html")


# ===== МАТЧИ =====
@app.route("/schedule")
def schedule():
    data = fetch_json(API_MATCHES)
    matches = []

    if not data or "data" not in data:
        return render_template("schedule.html", matches=[])

    now = datetime.utcnow()

    for m in data["data"]:
        start = parse_datetime(m["date"])

        matches.append({
            "id": m["id"],
            "team1": m["team1"]["name"],
            "team2": m["team2"]["name"],
            "time_iso": start.isoformat(),
            "time_display": start.strftime("%d.%m.%Y %H:%M"),
            "status": m["status"],  # 0 future | 1 live | 2 finished
        })

    # LIVE сверху, потом будущие
    matches.sort(key=lambda x: (x["status"] != 1, x["time_iso"]))

    return render_template("schedule.html", matches=matches)


# ===== РЕЗУЛЬТАТЫ =====
@app.route("/results")
def results():
    data = fetch_json(API_MATCHES)
    results_by_round = defaultdict(list)

    if not data or "data" not in data:
        return render_template("results.html", results_by_round={})

    for m in data["data"]:
        if m["status"] != 2:
            continue  # только завершённые

        round_id = m["connection"]["stage"]

        results_by_round[round_id].append({
            "team1": m["team1"]["name"],
            "team2": m["team2"]["name"],
            "score1": m["result1"],
            "score2": m["result2"],
            "winner": m["winner"]
        })

    # сортировка раундов
    results_by_round = dict(sorted(results_by_round.items()))

    return render_template(
        "results.html",
        results_by_round=results_by_round
    )


# ===== КОМАНДЫ =====
@app.route("/teams")
def teams():
    data = fetch_json(API_MATCHES)
    teams = {}

    if not data or "data" not in data:
        return render_template("teams.html", teams=[])

    for m in data["data"]:
        for t in [m["team1"], m["team2"]]:
            teams[t["id"]] = {
                "name": t["name"],
                "country": t["country"],
                "rating": t["rating"],
                "avatar": t["avatar"]
            }

    return render_template("teams.html", teams=teams.values())


# ===== СТАТИСТИКА =====
@app.route("/stats")
def stats():
    data = fetch_json(API_MATCHES)

    stats = {
        "total": 0,
        "finished": 0,
        "live": 0,
        "upcoming": 0
    }

    if not data or "data" not in data:
        return render_template("stats.html", stats=stats)

    stats["total"] = len(data["data"])

    for m in data["data"]:
        if m["status"] == 0:
            stats["upcoming"] += 1
        elif m["status"] == 1:
            stats["live"] += 1
        elif m["status"] == 2:
            stats["finished"] += 1

    return render_template("stats.html", stats=stats)


# ===== ЗАПУСК =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

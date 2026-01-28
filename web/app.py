import requests
from flask import Flask, render_template
from datetime import datetime, timezone
import os

app = Flask(__name__)

# ====== НАСТРОЙКИ ======
TOURNAMENT_ID = 842
API_TOURNAMENT = f"https://tankisport.com/api/tournaments/show/{TOURNAMENT_ID}"
API_TEAM = "https://tankisport.com/api/teams/show/{}"


# ====== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======

def fetch_tournament():
    try:
        r = requests.get(API_TOURNAMENT, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("API error:", e)
        return None


def parse_time(ts):
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return {
        "iso": dt.isoformat(),
        "display": dt.strftime("%d.%m.%Y %H:%M")
    }


# ====== ГЛАВНАЯ ======

@app.route("/")
def index():
    return render_template("index.html")


# ====== МАТЧИ ======

@app.route("/schedule")
def schedule():
    data = fetch_tournament()
    matches = []

    if data:
        for m in data.get("matches", []):
            # только незавершённые
            if m.get("winner") is None:
                t = parse_time(m["date"])
                matches.append({
                    "team1": m["team1"]["name"],
                    "team2": m["team2"]["name"],
                    "time_iso": t["iso"],
                    "time_display": t["display"]
                })

        # сортировка по времени
        matches.sort(key=lambda x: x["time_iso"])

    return render_template("schedule.html", matches=matches)


# ====== РЕЗУЛЬТАТЫ ======

@app.route("/results")
def results():
    data = fetch_tournament()
    results_by_round = {}

    if data:
        for m in data.get("matches", []):
            if m.get("winner") is not None:
                rnd = m.get("round", 1)

                results_by_round.setdefault(rnd, []).append({
                    "team1": m["team1"]["name"],
                    "team2": m["team2"]["name"],
                    "score1": m["result1"],
                    "score2": m["result2"]
                })

    # сортируем раунды
    results_by_round = dict(sorted(results_by_round.items()))

    return render_template(
        "results.html",
        results_by_round=results_by_round
    )


# ====== КОМАНДЫ ======

@app.route("/teams")
def teams():
    data = fetch_tournament()
    teams = []

    if data:
        team_ids = set()

        for m in data.get("matches", []):
            team_ids.add(m["team1"]["id"])
            team_ids.add(m["team2"]["id"])

        for tid in team_ids:
            try:
                r = requests.get(API_TEAM.format(tid), timeout=10)
                r.raise_for_status()
                t = r.json()
                teams.append({
                    "name": t["name"],
                    "tag": t.get("tag", ""),
                    "players": [p["nickname"] for p in t.get("players", [])]
                })
            except:
                continue

        teams.sort(key=lambda x: x["name"].lower())

    return render_template("teams.html", teams=teams)


# ====== СТАТИСТИКА ======

@app.route("/stats")
def stats():
    data = fetch_tournament()

    stats = {
        "total_matches": 0,
        "finished": 0,
        "live": 0,
        "upcoming": 0
    }

    if data:
        for m in data.get("matches", []):
            stats["total_matches"] += 1

            if m.get("winner") is not None:
                stats["finished"] += 1
            else:
                if m["date"] * 1000 <= datetime.utcnow().timestamp() * 1000:
                    stats["live"] += 1
                else:
                    stats["upcoming"] += 1

    return render_template("stats.html", stats=stats)


# ====== RUN (RENDER) ======

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

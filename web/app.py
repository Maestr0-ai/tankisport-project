import json
from flask import Flask, render_template
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# team_data.json лежит НА УРОВЕНЬ ВЫШЕ папки web
DATA_FILE = Path(__file__).resolve().parent.parent / "team_data.json"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    teams = data.get("team_states", {})
    tournament = data.get("tournament_states", {}).get("842", {})

    schedule = tournament.get("schedule", {})
    match_results = tournament.get("match_results", {})
    finished_ids = set(tournament.get("notified_results", []))

    return teams, schedule, match_results, finished_ids


# =========================
# Главная
# =========================
@app.route("/")
def index():
    return render_template("index.html")


# =========================
# МАТЧИ (будущие + LIVE)
# =========================
@app.route("/schedule")
def schedule_page():
    teams, schedule_data, _, finished_ids = load_data()
    matches = []

    for round_num, round_matches in schedule_data.items():
        if not isinstance(round_matches, list):
            continue

        for m in round_matches:
            match_id = str(m.get("match_id"))

            # ❗ ЕСЛИ матч уже есть в notified_results → он ЗАВЕРШЁН
            if match_id in finished_ids:
                continue

            teams_data = m.get("teams", {})
            t1_id = str(teams_data.get("team1_id"))
            t2_id = str(teams_data.get("team2_id"))

            match_time = datetime.strptime(
                m["time"],
                "%Y-%m-%d %H:%M:%S"
            )

            matches.append({
                "id": match_id,
                "round": round_num,
                "team1": teams.get(t1_id, {}).get("name", f"Team {t1_id}"),
                "team2": teams.get(t2_id, {}).get("name", f"Team {t2_id}"),
                "time_display": match_time.strftime("%d.%m.%Y %H:%M"),
                "time_iso": match_time.isoformat()
            })

    matches.sort(key=lambda x: x["time_iso"])
    return render_template("schedule.html", matches=matches)


# =========================
# РЕЗУЛЬТАТЫ (ТОЛЬКО ЗАВЕРШЁННЫЕ)
# =========================
@app.route("/results")
def results_page():
    _, _, results_data, _ = load_data()

    results_by_round = {}

    for round_num in range(1, 8):
        round_key = str(round_num)
        parsed = []

        for raw in results_data.get(round_key, []):
            # пример:
            # ⭐ **APEX ELITE** (1) — **EndGame** (3)
            try:
                clean = raw.replace("⭐", "").replace("**", "").strip()
                left, right = clean.split("—")

                team1, s1 = left.rsplit("(", 1)
                team2, s2 = right.rsplit("(", 1)

                score1 = int(s1.replace(")", "").strip())
                score2 = int(s2.replace(")", "").strip())

                parsed.append({
                    "team1": team1.strip(),
                    "team2": team2.strip(),
                    "score1": score1,
                    "score2": score2,
                    "winner": "team1" if score1 > score2 else "team2"
                })

            except Exception:
                continue

        results_by_round[round_num] = parsed

    return render_template(
        "results.html",
        results_by_round=results_by_round
    )


# =========================
# КОМАНДЫ
# =========================
@app.route("/teams")
def teams_page():
    teams, _, _, _ = load_data()
    return render_template("teams.html", teams=teams)


# =========================
# СТАТИСТИКА
# =========================
@app.route("/stats")
def stats_page():
    _, _, results, _ = load_data()
    return render_template("stats.html", results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

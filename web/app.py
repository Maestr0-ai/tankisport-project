import json
from flask import Flask, render_template
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# team_data.json лежит на уровень выше папки web
DATA_FILE = Path(__file__).resolve().parent.parent / "team_data.json"


def load_data():
    """
    Загружает данные и возвращает:
    - teams: словарь команд
    - schedule: расписание матчей
    - results: результаты матчей
    - finished_ids: ID завершённых матчей
    """
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    teams = data.get("team_states", {})
    tournament = data.get("tournament_states", {}).get("842", {})

    schedule = tournament.get("schedule", {})
    results = tournament.get("match_results", {})
    finished_ids = set(tournament.get("notified_results", []))

    return teams, schedule, results, finished_ids


@app.route("/")
def index():
    return render_template("index.html")


# ==================================================
# 📅 МАТЧИ
# - будущие
# - LIVE
# (завершённые сюда НЕ попадают)
# ==================================================
@app.route("/schedule")
def schedule_page():
    teams, schedule_data, _, finished_ids = load_data()
    matches = []

    for round_num, round_matches in schedule_data.items():
        if not isinstance(round_matches, list):
            continue

        for m in round_matches:
            match_id = str(m.get("match_id"))
            if match_id in finished_ids:
                # матч завершён → он будет в Results
                continue

            teams_data = m.get("teams", {})
            t1_id = str(teams_data.get("team1_id"))
            t2_id = str(teams_data.get("team2_id"))

            # парсим время матча
            match_time = datetime.strptime(
                m.get("time"),
                "%Y-%m-%d %H:%M:%S"
            )

            matches.append({
                "id": match_id,
                "round": round_num,
                "team1": teams.get(t1_id, {}).get("name", f"Team {t1_id}"),
                "team2": teams.get(t2_id, {}).get("name", f"Team {t2_id}"),

                # для отображения
                "time_display": match_time.strftime("%d.%m.%Y %H:%M"),

                # для JS таймеров (LIVE / countdown)
                "time_iso": match_time.isoformat()
            })

    # сортируем по времени (LIVE сами всплывут вверху через JS)
    matches.sort(key=lambda x: x["time_iso"])

    return render_template("schedule.html", matches=matches)


# ==================================================
# 🏆 РЕЗУЛЬТАТЫ (ТОЛЬКО ЗАВЕРШЁННЫЕ)
# ==================================================
@app.route("/results")
def results_page():
    _, _, results_data, _ = load_data()
    results_by_round = {}

    # фиксированные раунды 1–7
    for round_num in range(1, 8):
        round_key = str(round_num)
        parsed_results = []

        for raw in results_data.get(round_key, []):
            # ожидаемый формат строки:
            # ⭐ **Team A** (3) — **Team B** (1)
            try:
                clean = (
                    raw.replace("⭐", "")
                       .replace("**", "")
                       .strip()
                )

                left, right = clean.split("—")

                team1, s1 = left.rsplit("(", 1)
                team2, s2 = right.rsplit("(", 1)

                score1 = int(s1.replace(")", "").strip())
                score2 = int(s2.replace(")", "").strip())

                parsed_results.append({
                    "team1": team1.strip(),
                    "team2": team2.strip(),
                    "score1": score1,
                    "score2": score2
                })

            except Exception:
                # если формат строки битый — пропускаем
                continue

        results_by_round[round_num] = parsed_results

    return render_template(
        "results.html",
        results_by_round=results_by_round
    )


@app.route("/teams")
def teams_page():
    teams, _, _, _ = load_data()
    return render_template("teams.html", teams=teams)


@app.route("/stats")
def stats_page():
    _, _, results, _ = load_data()
    return render_template("stats.html", results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

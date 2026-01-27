import json
from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__)

DATA_FILE = Path(__file__).resolve().parent.parent / "team_data.json"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    teams = data.get("team_states", {})
    tournament = data.get("tournament_states", {}).get("842", {})

    schedule = tournament.get("schedule", {})
    results = tournament.get("match_results", {})

    finished_matches = set(tournament.get("notified_results", []))

    return teams, schedule, results, finished_matches


@app.route("/")
def index():
    return render_template("index.html")


# ======================
# 📅 МАТЧИ (АКТИВНЫЕ)
# ======================
@app.route("/schedule")
def schedule_page():
    teams, schedule_data, _, finished = load_data()
    matches = []

    for round_num, round_matches in schedule_data.items():
        if not isinstance(round_matches, list):
            continue

        for m in round_matches:
            match_id = str(m.get("match_id"))
            if match_id in finished:
                continue  # убираем завершённые

            t = m.get("teams", {})
            t1 = str(t.get("team1_id"))
            t2 = str(t.get("team2_id"))

            matches.append({
                "round": round_num,
                "time": m.get("time"),
                "team1": teams.get(t1, {}).get("name", f"Team {t1}"),
                "team2": teams.get(t2, {}).get("name", f"Team {t2}")
            })

    return render_template("schedule.html", matches=matches)


# ======================
# 🏆 РЕЗУЛЬТАТЫ
# ======================
@app.route("/results")
def results_page():
    teams, _, results_data, _ = load_data()
    results_by_round = {}

    for r in range(1, 8):
        r_key = str(r)
        round_results = []

        for raw in results_data.get(r_key, []):
            # пример строки:
            # "TeamA (3) — TeamB (1)"

            try:
                left, right = raw.split("—")
                team1, s1 = left.rsplit("(", 1)
                team2, s2 = right.rsplit("(", 1)

                score1 = int(s1.replace(")", "").strip())
                score2 = int(s2.replace(")", "").strip())

                round_results.append({
                    "team1": team1.strip(),
                    "team2": team2.strip(),
                    "score1": score1,
                    "score2": score2,
                })
            except Exception:
                continue

        results_by_round[r] = round_results

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

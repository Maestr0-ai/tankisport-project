import json
from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__)

# team_data.json лежит НА УРОВЕНЬ ВЫШЕ папки web
DATA_FILE = Path(__file__).resolve().parent.parent / "team_data.json"


def load_data():
    if not DATA_FILE.exists():
        print("❌ team_data.json NOT FOUND:", DATA_FILE)
        return {}, {}, {}, {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    teams = data.get("team_states", {})
    tournament = data.get("tournament_states", {}).get("842", {})

    schedule = tournament.get("schedule", {})
    results = tournament.get("match_results", {})

    notified_results = set(tournament.get("notified_results", []))

    return teams, schedule, results, notified_results


@app.route("/")
def index():
    return render_template("index.html")


# =========================
# 📅 МАТЧИ (ТОЛЬКО АКТИВНЫЕ)
# =========================
@app.route("/schedule")
def schedule():
    teams, schedule_data, _, finished_matches = load_data()

    matches = []

    for round_num, round_matches in schedule_data.items():
        if not isinstance(round_matches, list):
            continue

        for match in round_matches:
            match_id = str(match.get("match_id"))

            # ❗ если матч уже завершён — НЕ ПОКАЗЫВАЕМ
            if match_id in finished_matches:
                continue

            t = match.get("teams", {})
            team1_id = str(t.get("team1_id", ""))
            team2_id = str(t.get("team2_id", ""))

            matches.append({
                "round": round_num,
                "time": match.get("time", ""),
                "team1": teams.get(team1_id, {}).get("name", f"Team {team1_id}"),
                "team2": teams.get(team2_id, {}).get("name", f"Team {team2_id}"),
            })

    return render_template("schedule.html", matches=matches)


# =========================
# 🏆 РЕЗУЛЬТАТЫ ПО РАУНДАМ
# =========================
@app.route("/results")
def results():
    teams, _, results_data, _ = load_data()

    results_by_round = {}

    # Раунды 1–7
    for round_num in range(1, 8):
        round_key = str(round_num)
        round_results = []

        matches = results_data.get(round_key, [])

        for m in matches:
            # строка уже готовая: "Team (3) — Team (1)"
            round_results.append(m)

        results_by_round[round_num] = round_results

    return render_template(
        "results.html",
        results_by_round=results_by_round
    )


@app.route("/teams")
def teams_page():
    teams, _, _, _ = load_data()
    return render_template("teams.html", teams=teams)


@app.route("/stats")
def stats():
    _, _, results_data, _ = load_data()
    return render_template("stats.html", results=results_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

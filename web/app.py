from flask import Flask, render_template
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(filename):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/schedule")
def schedule():
    data = load_json("tournament_progress.json")
    return render_template("schedule.html", data=data)

@app.route("/teams")
def teams():
    data = load_json("team_data.json")
    return render_template("teams.html", data=data)

@app.route("/stats")
def stats():
    data = load_json("team_history.json")
    return render_template("stats.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

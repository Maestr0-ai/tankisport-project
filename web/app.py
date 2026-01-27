from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

@app.route("/")
def index():
    return "TankiSport web panel is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

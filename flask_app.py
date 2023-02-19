from flask import Flask, jsonify
from flask_caching import Cache
import requests
from bs4 import BeautifulSoup
import sqlite3
import time

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'memory'})

@cache.cached(timeout=60)
def update_leaderboard():
    URL = "https://www.espn.com/golf/leaderboard"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    players = soup.find_all("tr", class_="Table2__tr")
    leaderboard = []

    for player in players:
        player_data = player.find_all("td")
        rank = player_data[0].text
        name = player_data[1].text
        score = player_data[4].text

        leaderboard.append((rank, name, score))

    return leaderboard

def update_database(leaderboard):
    conn = sqlite3.connect("leaderboard.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS players (rank TEXT, name TEXT, score TEXT)")
    c.executemany("INSERT INTO players (rank, name, score) VALUES (?, ?, ?)", leaderboard)

    conn.commit()
    conn.close()

@app.route("/leaderboard")
def get_leaderboard():
    leaderboard = update_leaderboard()
    update_database(leaderboard)

    return jsonify(leaderboard)

if __name__ == "__main__":
    app.run(debug=True)

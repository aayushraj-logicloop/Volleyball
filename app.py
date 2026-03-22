from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('players.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            position TEXT,
            rating INTEGER
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------- GET PLAYERS ----------
def get_players():
    conn = sqlite3.connect('players.db')
    c = conn.cursor()

    c.execute("SELECT * FROM players")
    players = c.fetchall()

    conn.close()
    return players

# ---------- ADD PLAYER ----------
@app.route("/add", methods=["POST"])
def add_player():
    name = request.form["name"]
    position = request.form["position"]
    rating = int(request.form["rating"])

    conn = sqlite3.connect('players.db')
    c = conn.cursor()

    c.execute("INSERT INTO players (name, position, rating) VALUES (?, ?, ?)",
              (name, position, rating))

    conn.commit()
    conn.close()

    return redirect("/")

# ---------- HOME ----------
@app.route("/")
def home():
    players = get_players()
    return render_template("index.html", players=players, team_a=None, team_b=None)

# ---------- TEAM GENERATION ----------
@app.route("/generate", methods=["POST"])
def generate():
    selected_ids = request.form.getlist("players")

    if not selected_ids:
        return redirect("/")

    conn = sqlite3.connect('players.db')
    c = conn.cursor()

    query = f"SELECT * FROM players WHERE id IN ({','.join(['?']*len(selected_ids))})"
    c.execute(query, selected_ids)
    players = c.fetchall()

    conn.close()

    # Convert to dict
    players_list = []
    for p in players:
        players_list.append({
            "id": p[0],
            "name": p[1],
            "position": p[2],
            "rating": p[3]
        })

    # ---- BALANCING LOGIC ----
    players_list = sorted(players_list, key=lambda x: x["rating"], reverse=True)

    team_a = []
    team_b = []
    sum_a = 0
    sum_b = 0

    for player in players_list:
        if sum_a <= sum_b:
            team_a.append(player)
            sum_a += player["rating"]
        else:
            team_b.append(player)
            sum_b += player["rating"]

    all_players = get_players()

    return render_template("index.html",
                           players=all_players,
                           team_a=team_a,
                           team_b=team_b,
                           sum_a=sum_a,
                           sum_b=sum_b)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run()

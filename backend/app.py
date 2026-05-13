from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=os.environ.get('CORS_ORIGINS', '*').split(','))

# DB lives in a mounted volume in production
DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'data', 'hunting.db'))


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS hunters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS game_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hunter_id INTEGER NOT NULL,
            species TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 1,
            hunt_date TEXT NOT NULL,
            location TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (hunter_id) REFERENCES hunters(id)
        );

        CREATE TABLE IF NOT EXISTS saved_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            filters TEXT NOT NULL,
            chart_type TEXT DEFAULT 'bar',
            created_at TEXT DEFAULT (datetime('now'))
        );
    ''')

    # Seed sample data only if DB is empty
    if c.execute("SELECT COUNT(*) FROM hunters").fetchone()[0] == 0:
        seed_data(c)

    conn.commit()
    conn.close()


def seed_data(c):
    import random
    hunters = [('Erik Larsson',), ('Maja Svensson',), ('Björn Nilsson',),
               ('Ingrid Karlsson',), ('Lars Andersson',)]
    c.executemany("INSERT INTO hunters (name) VALUES (?)", hunters)

    species_list = ['Moose', 'Roe Deer', 'Wild Boar', 'Pheasant',
                    'Mallard', 'Hare', 'Fox', 'Red Deer']
    locations = ['North Forest', 'Lake Area', 'South Ridge', 'Valley', 'East Marshes']

    for hunter_id in range(1, 6):
        for _ in range(random.randint(8, 20)):
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            year = random.choice([2023, 2024, 2025])
            c.execute(
                "INSERT INTO game_log (hunter_id, species, count, hunt_date, location) VALUES (?,?,?,?,?)",
                (hunter_id, random.choice(species_list), random.randint(1, 3),
                 f"{year}-{month:02d}-{day:02d}", random.choice(locations))
            )


# ── Health check ─────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'db': DB_PATH})


# ── Hunters ──────────────────────────────────────────────
@app.route('/api/hunters', methods=['GET'])
def get_hunters():
    conn = get_db()
    hunters = conn.execute("SELECT * FROM hunters ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(h) for h in hunters])


@app.route('/api/hunters', methods=['POST'])
def add_hunter():
    data = request.json
    if not data or not data.get('name', '').strip():
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    try:
        conn.execute("INSERT INTO hunters (name) VALUES (?)", (data['name'].strip(),))
        conn.commit()
        hunter = conn.execute("SELECT * FROM hunters WHERE name=?", (data['name'].strip(),)).fetchone()
        conn.close()
        return jsonify(dict(hunter)), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Hunter already exists'}), 409


@app.route('/api/hunters/<int:hunter_id>', methods=['DELETE'])
def delete_hunter(hunter_id):
    conn = get_db()
    conn.execute("DELETE FROM game_log WHERE hunter_id=?", (hunter_id,))
    conn.execute("DELETE FROM hunters WHERE id=?", (hunter_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Game log ─────────────────────────────────────────────
@app.route('/api/game', methods=['GET'])
def get_game():
    conn = get_db()
    rows = conn.execute('''
        SELECT g.*, h.name as hunter_name
        FROM game_log g JOIN hunters h ON g.hunter_id = h.id
        ORDER BY g.hunt_date DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/game', methods=['POST'])
def add_game():
    data = request.json
    required = ['hunter_id', 'species', 'hunt_date']
    if not data or not all(data.get(k) for k in required):
        return jsonify({'error': 'hunter_id, species and hunt_date are required'}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO game_log (hunter_id, species, count, hunt_date, location, notes) VALUES (?,?,?,?,?,?)",
        (data['hunter_id'], data['species'].strip(), int(data.get('count', 1)),
         data['hunt_date'], data.get('location', ''), data.get('notes', ''))
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201


@app.route('/api/game/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    conn = get_db()
    conn.execute("DELETE FROM game_log WHERE id=?", (game_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Stats ─────────────────────────────────────────────────
@app.route('/api/stats/leaderboard')
def leaderboard():
    hunter_ids = request.args.getlist('hunter_ids')
    species    = request.args.getlist('species')
    locations  = request.args.getlist('locations')
    year_from  = request.args.get('year_from')
    year_to    = request.args.get('year_to')
    group_by   = request.args.get('group_by', 'hunter')

    conditions, params = [], []
    if hunter_ids:
        conditions.append(f"g.hunter_id IN ({','.join('?'*len(hunter_ids))})")
        params.extend(hunter_ids)
    if species:
        conditions.append(f"g.species IN ({','.join('?'*len(species))})")
        params.extend(species)
    if locations:
        conditions.append(f"g.location IN ({','.join('?'*len(locations))})")
        params.extend(locations)
    if year_from:
        conditions.append("strftime('%Y', g.hunt_date) >= ?"); params.append(year_from)
    if year_to:
        conditions.append("strftime('%Y', g.hunt_date) <= ?"); params.append(year_to)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    if group_by == 'species':
        query = f"SELECT g.species as label, SUM(g.count) as total FROM game_log g JOIN hunters h ON g.hunter_id=h.id {where} GROUP BY g.species ORDER BY total DESC"
    else:
        query = f"SELECT h.name as label, SUM(g.count) as total, h.id as hunter_id FROM game_log g JOIN hunters h ON g.hunter_id=h.id {where} GROUP BY g.hunter_id ORDER BY total DESC"

    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/stats/species')
def species_list():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT species FROM game_log ORDER BY species").fetchall()
    conn.close()
    return jsonify([r['species'] for r in rows])


@app.route('/api/stats/locations')
def locations_list():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT location FROM game_log WHERE location != '' ORDER BY location").fetchall()
    conn.close()
    return jsonify([r['location'] for r in rows])


# ── Saved views ───────────────────────────────────────────
@app.route('/api/views', methods=['GET'])
def get_views():
    conn = get_db()
    rows = conn.execute("SELECT * FROM saved_views ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/views', methods=['POST'])
def save_view():
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO saved_views (name, filters, chart_type) VALUES (?,?,?)",
        (data['name'], json.dumps(data.get('filters', {})), data.get('chart_type', 'bar'))
    )
    conn.commit()
    view = conn.execute("SELECT * FROM saved_views ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return jsonify(dict(view)), 201


@app.route('/api/views/<int:view_id>', methods=['DELETE'])
def delete_view(view_id):
    conn = get_db()
    conn.execute("DELETE FROM saved_views WHERE id=?", (view_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Entry point ───────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5050, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')

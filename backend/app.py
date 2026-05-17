from flask import Flask, jsonify, request, make_response, session
from flask_cors import CORS
import sqlite3
import os
import json
import secrets
from datetime import datetime, timedelta
from functools import wraps

import bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.environ.get('SESSION_HOURS', '12')))

CORS(app, origins=os.environ.get('CORS_ORIGINS', '*').split(','), supports_credentials=True)

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
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer',
            created_at TEXT DEFAULT (datetime('now')),
            last_login TEXT,
            disabled INTEGER NOT NULL DEFAULT 0,
            hunter_id INTEGER
        );
        CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS hunter_associations (
            hunter_id INTEGER NOT NULL,
            association_id INTEGER NOT NULL,
            PRIMARY KEY (hunter_id, association_id)
        );
        CREATE TABLE IF NOT EXISTS user_associations (
            user_id INTEGER NOT NULL,
            association_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, association_id)
        );
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
        CREATE TABLE IF NOT EXISTS embed_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            mode TEXT NOT NULL DEFAULT 'leaderboard',
            view_id INTEGER,
            params TEXT NOT NULL DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now')),
            last_used TEXT,
            use_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS saved_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            filters TEXT NOT NULL,
            chart_type TEXT DEFAULT 'bar',
            created_at TEXT DEFAULT (datetime('now')),
            owner_id INTEGER,
            is_private INTEGER NOT NULL DEFAULT 0
        );
    ''')

    # Migrations: add columns to existing DBs
    cols = [r[1] for r in c.execute("PRAGMA table_info(users)").fetchall()]
    if 'disabled' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN disabled INTEGER NOT NULL DEFAULT 0")
    if 'hunter_id' not in cols:
        c.execute("ALTER TABLE users ADD COLUMN hunter_id INTEGER")
    vcols = [r[1] for r in c.execute("PRAGMA table_info(saved_views)").fetchall()]
    if 'owner_id' not in vcols:
        c.execute("ALTER TABLE saved_views ADD COLUMN owner_id INTEGER")
    if 'is_private' not in vcols:
        c.execute("ALTER TABLE saved_views ADD COLUMN is_private INTEGER NOT NULL DEFAULT 0")

    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        default_pw = os.environ.get('ADMIN_PASSWORD', 'changeme')
        pw_hash = bcrypt.hashpw(default_pw.encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
                  ('admin', pw_hash, 'admin'))
        print(f"[wildlog] Default admin created. Password: {default_pw}  <-- CHANGE THIS!")

    if c.execute("SELECT COUNT(*) FROM hunters").fetchone()[0] == 0:
        seed_data(c)

    conn.commit()
    conn.close()


def seed_data(c):
    import random
    hunters = [('Erik Larsson',), ('Maja Svensson',), ('Bjorn Nilsson',),
               ('Ingrid Karlsson',), ('Lars Andersson',)]
    c.executemany("INSERT INTO hunters (name) VALUES (?)", hunters)
    species_list = ['Moose','Roe Deer','Wild Boar','Pheasant','Mallard','Hare','Fox','Red Deer']
    locations    = ['North Forest','Lake Area','South Ridge','Valley','East Marshes']
    for hunter_id in range(1, 6):
        for _ in range(random.randint(8, 20)):
            month = random.randint(1, 12)
            day   = random.randint(1, 28)
            year  = random.choice([2023, 2024, 2025])
            c.execute(
                "INSERT INTO game_log (hunter_id,species,count,hunt_date,location) VALUES(?,?,?,?,?)",
                (hunter_id, random.choice(species_list), random.randint(1,3),
                 f"{year}-{month:02d}-{day:02d}", random.choice(locations))
            )


# ── Auth decorators ───────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Authentication required', 'login': True}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Authentication required', 'login': True}), 401
        if session.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

def assoc_admin_or_above(f):
    """Allow admin and assoc_admin roles."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Authentication required', 'login': True}), 401
        if session.get('role') not in ('admin', 'assoc_admin'):
            return jsonify({'error': 'Association admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


def any_active_role(f):
    """Allow admin, assoc_admin, and user — not viewer."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Authentication required', 'login': True}), 401
        if session.get('role') not in ('admin', 'assoc_admin', 'user'):
            return jsonify({'error': 'Access denied'}), 403
        return f(*args, **kwargs)
    return decorated


def user_or_admin_required(f):
    """Allow admins and users (role='user') but not viewers."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Authentication required', 'login': True}), 401
        if session.get('role') not in ('admin', 'user'):
            return jsonify({'error': 'Access denied'}), 403
        return f(*args, **kwargs)
    return decorated


def cors_public(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['X-Frame-Options'] = 'ALLOWALL'
        return resp
    return decorated


# ── Auth ─────────────────────────────────────────────────

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    if user and bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        if user['disabled']:
            conn.close()
            return jsonify({'error': 'This account has been disabled'}), 403
        conn.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user['id'],))
        conn.commit()
        conn.close()
        session.permanent = True
        session['user_id']   = user['id']
        session['username']  = user['username']
        session['role']      = user['role']
        session['hunter_id'] = user['hunter_id']
        return jsonify({'id': user['id'], 'username': user['username'], 'role': user['role']})
    conn.close()
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me')
def me():
    if not session.get('user_id'):
        return jsonify({'authenticated': False}), 401
    conn = get_db()
    user = conn.execute("SELECT hunter_id FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()
    hunter_id = user['hunter_id'] if user else None
    return jsonify({'authenticated': True, 'id': session['user_id'], 'username': session['username'], 'role': session['role'], 'hunter_id': hunter_id, 'site_assoc_id': session.get('site_assoc_id')})


# ── Users ────────────────────────────────────────────────

@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    conn = get_db()
    rows = conn.execute(
        "SELECT id,username,role,created_at,last_login,disabled,hunter_id FROM users ORDER BY username"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '')
    role     = data.get('role', 'viewer')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if role not in ('admin', 'assoc_admin', 'viewer', 'user'):
        return jsonify({'error': 'Role must be admin, assoc_admin, viewer or user'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username,password_hash,role) VALUES(?,?,?)",
                     (username, pw_hash, role))
        conn.commit()
        user = conn.execute(
            "SELECT id,username,role,created_at FROM users WHERE username=?", (username,)
        ).fetchone()
        conn.close()
        return jsonify(dict(user)), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 409

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/users/<int:user_id>/password', methods=['POST'])
@login_required
def change_password(user_id):
    if session['role'] != 'admin' and session['user_id'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json or {}
    new_pw = data.get('password', '')
    if len(new_pw) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    pw_hash = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
    conn = get_db()
    conn.execute("UPDATE users SET password_hash=? WHERE id=?", (pw_hash, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/users/<int:user_id>/hunter', methods=['POST'])
@admin_required
def set_user_hunter(user_id):
    data = request.json or {}
    hunter_id = data.get('hunter_id')  # None to unlink
    conn = get_db()
    conn.execute("UPDATE users SET hunter_id=? WHERE id=?", (hunter_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/users/<int:user_id>/role', methods=['POST'])
@admin_required
def change_role(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': 'Cannot change your own role'}), 400
    data = request.json or {}
    role = data.get('role')
    if role not in ('admin', 'assoc_admin', 'viewer', 'user'):
        return jsonify({'error': 'Role must be admin, assoc_admin, viewer or user'}), 400
    conn = get_db()
    conn.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/users/<int:user_id>/disabled', methods=['POST'])
@admin_required
def set_disabled(user_id):
    if user_id == session['user_id']:
        return jsonify({'error': 'Cannot disable your own account'}), 400
    data = request.json or {}
    disabled = 1 if data.get('disabled') else 0
    conn = get_db()
    conn.execute("UPDATE users SET disabled=? WHERE id=?", (disabled, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})



def get_assoc_filter(conn, association_id=None):
    role = session.get('role')
    uid  = session.get('user_id')
    if association_id is None:
        association_id = session.get('site_assoc_id')

    if role == 'admin' and not association_id:
        return '', [], []

    if role == 'admin' and association_id:
        return (
            "JOIN hunter_associations ha_f ON ha_f.hunter_id = h.id",
            ["ha_f.association_id = ?"],
            [association_id]
        )

    # non-admin: verify membership if specific assoc requested
    if association_id:
        ok = conn.execute(
            "SELECT 1 FROM user_associations WHERE user_id=? AND association_id=?",
            (uid, association_id)
        ).fetchone()
        if not ok:
            association_id = None

    if association_id:
        return (
            "JOIN hunter_associations ha_f ON ha_f.hunter_id = h.id",
            ["ha_f.association_id = ?"],
            [association_id]
        )
    else:
        return (
            "JOIN hunter_associations ha_f ON ha_f.hunter_id = h.id "
            "JOIN user_associations ua_f ON ua_f.association_id = ha_f.association_id AND ua_f.user_id = ?",
            [],
            [uid]
        )


@app.route('/api/associations', methods=['GET'])
@login_required
def get_associations():
    conn = get_db()
    role = session.get('role')
    uid  = session.get('user_id')
    if role == 'admin':
        rows = conn.execute(
            "SELECT a.*, COUNT(DISTINCT ha.hunter_id) as hunter_count, COUNT(DISTINCT ua.user_id) as user_count "
            "FROM associations a "
            "LEFT JOIN hunter_associations ha ON ha.association_id=a.id "
            "LEFT JOIN user_associations ua ON ua.association_id=a.id "
            "GROUP BY a.id ORDER BY a.name"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT a.*, COUNT(DISTINCT ha.hunter_id) as hunter_count, COUNT(DISTINCT ua.user_id) as user_count "
            "FROM associations a "
            "JOIN user_associations ua2 ON ua2.association_id=a.id AND ua2.user_id=? "
            "LEFT JOIN hunter_associations ha ON ha.association_id=a.id "
            "LEFT JOIN user_associations ua ON ua.association_id=a.id "
            "GROUP BY a.id ORDER BY a.name",
            (uid,)
        ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/associations', methods=['POST'])
@admin_required
def create_association():
    data = request.json or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    try:
        conn.execute("INSERT INTO associations (name) VALUES (?)", (name,))
        conn.commit()
        row = conn.execute("SELECT * FROM associations WHERE name=?", (name,)).fetchone()
        conn.close()
        return jsonify(dict(row)), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Association already exists'}), 409


@app.route('/api/associations/<int:assoc_id>', methods=['PUT'])
@admin_required
def update_association(assoc_id):
    data = request.json or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    try:
        conn.execute("UPDATE associations SET name=? WHERE id=?", (name, assoc_id))
        conn.commit()
        row = conn.execute("SELECT * FROM associations WHERE id=?", (assoc_id,)).fetchone()
        conn.close()
        return jsonify(dict(row))
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Name already exists'}), 409


@app.route('/api/associations/<int:assoc_id>', methods=['DELETE'])
@admin_required
def delete_association(assoc_id):
    conn = get_db()
    conn.execute("DELETE FROM hunter_associations WHERE association_id=?", (assoc_id,))
    conn.execute("DELETE FROM user_associations WHERE association_id=?", (assoc_id,))
    conn.execute("DELETE FROM associations WHERE id=?", (assoc_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/associations/<int:assoc_id>/hunters', methods=['GET'])
@login_required
def get_assoc_hunters(assoc_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM hunter_associations WHERE association_id=?", (assoc_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/associations/<int:assoc_id>/users', methods=['GET'])
@login_required
def get_assoc_users(assoc_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM user_associations WHERE association_id=?", (assoc_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/associations/<int:assoc_id>/members', methods=['POST'])
@admin_required
def set_assoc_members(assoc_id):
    data = request.json or {}
    hunter_ids = data.get('hunter_ids', [])
    user_ids   = data.get('user_ids', [])
    conn = get_db()
    conn.execute("DELETE FROM hunter_associations WHERE association_id=?", (assoc_id,))
    conn.execute("DELETE FROM user_associations WHERE association_id=?", (assoc_id,))
    for hid in hunter_ids:
        conn.execute("INSERT OR IGNORE INTO hunter_associations (hunter_id,association_id) VALUES (?,?)", (hid, assoc_id))
    for uid in user_ids:
        conn.execute("INSERT OR IGNORE INTO user_associations (user_id,association_id) VALUES (?,?)", (uid, assoc_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/session/association', methods=['POST'])
@login_required
def set_session_association():
    data = request.json or {}
    assoc_id = data.get('association_id')
    if assoc_id:
        if session.get('role') != 'admin':
            conn = get_db()
            ok = conn.execute(
                "SELECT 1 FROM user_associations WHERE user_id=? AND association_id=?",
                (session['user_id'], assoc_id)
            ).fetchone()
            conn.close()
            if not ok:
                return jsonify({'error': 'Not a member of that association'}), 403
    session['site_assoc_id'] = assoc_id
    return jsonify({'success': True, 'association_id': assoc_id})


@app.route('/api/hunters/<int:hunter_id>/associations', methods=['GET'])
@login_required
def get_hunter_associations(hunter_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT a.* FROM associations a "
        "JOIN hunter_associations ha ON ha.association_id=a.id "
        "WHERE ha.hunter_id=? ORDER BY a.name",
        (hunter_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/hunters/<int:hunter_id>/associations', methods=['POST'])
@admin_required
def set_hunter_associations(hunter_id):
    data = request.json or {}
    assoc_ids = data.get('association_ids', [])
    conn = get_db()
    conn.execute("DELETE FROM hunter_associations WHERE hunter_id=?", (hunter_id,))
    for aid in assoc_ids:
        conn.execute("INSERT OR IGNORE INTO hunter_associations (hunter_id,association_id) VALUES (?,?)",
                     (hunter_id, aid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/users/<int:user_id>/associations', methods=['GET'])
@login_required
def get_user_associations(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT a.* FROM associations a "
        "JOIN user_associations ua ON ua.association_id=a.id "
        "WHERE ua.user_id=? ORDER BY a.name",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/users/<int:user_id>/associations', methods=['POST'])
@admin_required
def set_user_associations(user_id):
    data = request.json or {}
    assoc_ids = data.get('association_ids', [])
    conn = get_db()
    conn.execute("DELETE FROM user_associations WHERE user_id=?", (user_id,))
    for aid in assoc_ids:
        conn.execute("INSERT OR IGNORE INTO user_associations (user_id,association_id) VALUES (?,?)",
                     (user_id, aid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── Health ────────────────────────────────────────────────

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})


# ── Hunters ───────────────────────────────────────────────

@app.route('/api/hunters', methods=['GET'])
@login_required
def get_hunters():
    conn = get_db()
    assoc_id = request.args.get('association_id', type=int)
    aj, ac, ap = get_assoc_filter(conn, assoc_id)
    if aj:
        where = ("WHERE " + " AND ".join(ac)) if ac else ""
        q = (
            "SELECT DISTINCT h.*, "
            "GROUP_CONCAT(DISTINCT a2.name) as associations "
            "FROM hunters h " + aj + " "
            "LEFT JOIN hunter_associations ha2 ON ha2.hunter_id=h.id "
            "LEFT JOIN associations a2 ON a2.id=ha2.association_id "
            + where + " GROUP BY h.id ORDER BY h.name"
        )
        rows = conn.execute(q, ap).fetchall()
    else:
        rows = conn.execute(
            "SELECT h.*, GROUP_CONCAT(DISTINCT a.name) as associations "
            "FROM hunters h "
            "LEFT JOIN hunter_associations ha ON ha.hunter_id=h.id "
            "LEFT JOIN associations a ON a.id=ha.association_id "
            "GROUP BY h.id ORDER BY h.name"
        ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/hunters', methods=['POST'])
@assoc_admin_or_above
def add_hunter():
    data = request.json
    if not data or not data.get('name', '').strip():
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    try:
        conn.execute("INSERT INTO hunters (name) VALUES (?)", (data['name'].strip(),))
        conn.commit()
        hunter = conn.execute("SELECT * FROM hunters WHERE name=?", (data['name'].strip(),)).fetchone()
        # assoc_admin: auto-assign new hunter to their active association
        if session.get('role') == 'assoc_admin':
            assoc_id = session.get('site_assoc_id')
            if assoc_id:
                conn.execute("INSERT OR IGNORE INTO hunter_associations (hunter_id,association_id) VALUES (?,?)",
                             (hunter['id'], assoc_id))
                conn.commit()
        conn.close()
        return jsonify(dict(hunter)), 201
    except sqlite3.IntegrityError:
        conn.close()
        # Return a specific code so frontend can distinguish "exists" from other errors
        return jsonify({'error': 'Hunter already exists', 'code': 'hunter_exists'}), 409

@app.route('/api/hunters/<int:hunter_id>', methods=['PUT'])
@assoc_admin_or_above
def update_hunter(hunter_id):
    data = request.json or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    if session.get('role') == 'assoc_admin':
        assoc_id = session.get('site_assoc_id')
        linked = conn.execute("SELECT 1 FROM hunter_associations WHERE hunter_id=? AND association_id=?",
                              (hunter_id, assoc_id)).fetchone()
        if not linked:
            conn.close()
            return jsonify({'error': 'Hunter not in your association'}), 403
    try:
        conn.execute("UPDATE hunters SET name=? WHERE id=?", (name, hunter_id))
        conn.commit()
        hunter = conn.execute("SELECT * FROM hunters WHERE id=?", (hunter_id,)).fetchone()
        conn.close()
        return jsonify(dict(hunter))
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'A hunter with that name already exists'}), 409


@app.route('/api/hunters/<int:hunter_id>/unassign', methods=['POST'])
@assoc_admin_or_above
def unassign_hunter(hunter_id):
    """Remove a hunter from the assoc_admin's active association (does not delete the hunter)."""
    if session.get('role') != 'assoc_admin':
        return jsonify({'error': 'Use DELETE to remove hunter entirely'}), 400
    assoc_id = session.get('site_assoc_id')
    if not assoc_id:
        return jsonify({'error': 'No active association selected'}), 400
    conn = get_db()
    conn.execute("DELETE FROM hunter_associations WHERE hunter_id=? AND association_id=?",
                 (hunter_id, assoc_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/hunters/<int:hunter_id>', methods=['DELETE'])
@admin_required
def delete_hunter(hunter_id):
    conn = get_db()
    conn.execute("DELETE FROM game_log WHERE hunter_id=?", (hunter_id,))
    conn.execute("DELETE FROM hunters WHERE id=?", (hunter_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Game log ──────────────────────────────────────────────

@app.route('/api/game', methods=['GET'])
@login_required
def get_game():
    conn = get_db()
    assoc_id = request.args.get('association_id', type=int)
    aj, ac, ap = get_assoc_filter(conn, assoc_id)
    where = ("WHERE " + " AND ".join(ac)) if ac else ""
    q = f"SELECT DISTINCT g.*, h.name as hunter_name FROM game_log g JOIN hunters h ON g.hunter_id=h.id {aj} {where} ORDER BY g.hunt_date DESC"
    rows = conn.execute(q, ap).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/game', methods=['POST'])
@any_active_role
def add_game():
    data = request.json
    if not data or not all(data.get(k) for k in ['hunter_id','species','hunt_date']):
        return jsonify({'error': 'hunter_id, species and hunt_date are required'}), 400

    role = session.get('role')
    if role == 'user':
        conn = get_db()
        user_row = conn.execute("SELECT hunter_id FROM users WHERE id=?", (session['user_id'],)).fetchone()
        conn.close()
        if not user_row or not user_row['hunter_id']:
            return jsonify({'error': 'Your account is not linked to a hunter. Ask an admin to link your account.'}), 403
        if int(data['hunter_id']) != user_row['hunter_id']:
            return jsonify({'error': 'You can only log game for your own hunter.'}), 403
    elif role == 'assoc_admin':
        assoc_id = session.get('site_assoc_id')
        if not assoc_id:
            return jsonify({'error': 'Select an active association first.'}), 400
        conn = get_db()
        linked = conn.execute("SELECT 1 FROM hunter_associations WHERE hunter_id=? AND association_id=?",
                              (int(data['hunter_id']), assoc_id)).fetchone()
        conn.close()
        if not linked:
            return jsonify({'error': 'Hunter is not in your active association.'}), 403

    conn = get_db()
    conn.execute(
        "INSERT INTO game_log (hunter_id,species,count,hunt_date,location,notes) VALUES(?,?,?,?,?,?)",
        (data['hunter_id'], data['species'].strip(), int(data.get('count',1)),
         data['hunt_date'], data.get('location',''), data.get('notes',''))
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

@app.route('/api/game/<int:game_id>', methods=['DELETE'])
@any_active_role
def delete_game(game_id):
    conn = get_db()
    role = session.get('role')
    entry = conn.execute("SELECT hunter_id FROM game_log WHERE id=?", (game_id,)).fetchone()
    if not entry:
        conn.close()
        return jsonify({'error': 'Entry not found'}), 404
    if role == 'user':
        user_row = conn.execute("SELECT hunter_id FROM users WHERE id=?", (session['user_id'],)).fetchone()
        hunter_id = user_row['hunter_id'] if user_row else None
        if not hunter_id or entry['hunter_id'] != hunter_id:
            conn.close()
            return jsonify({'error': 'You can only delete your own entries'}), 403
    elif role == 'assoc_admin':
        assoc_id = session.get('site_assoc_id')
        linked = conn.execute("SELECT 1 FROM hunter_associations WHERE hunter_id=? AND association_id=?",
                              (entry['hunter_id'], assoc_id)).fetchone()
        if not linked:
            conn.close()
            return jsonify({'error': 'You can only delete entries for hunters in your association'}), 403
    conn.execute("DELETE FROM game_log WHERE id=?", (game_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Stats ─────────────────────────────────────────────────

@app.route('/api/stats/leaderboard')
@login_required
def leaderboard():
    hunter_ids = request.args.getlist('hunter_ids')
    species    = request.args.getlist('species')
    locations  = request.args.getlist('locations')
    year_from  = request.args.get('year_from')
    year_to    = request.args.get('year_to')
    group_by   = request.args.get('group_by', 'hunter')
    conditions, params = [], []
    if hunter_ids:
        conditions.append(f"g.hunter_id IN ({','.join('?'*len(hunter_ids))})"); params.extend(hunter_ids)
    if species:
        conditions.append(f"g.species IN ({','.join('?'*len(species))})"); params.extend(species)
    if locations:
        conditions.append(f"g.location IN ({','.join('?'*len(locations))})"); params.extend(locations)
    if year_from:
        conditions.append("strftime('%Y',g.hunt_date)>=?"); params.append(year_from)
    if year_to:
        conditions.append("strftime('%Y',g.hunt_date)<=?"); params.append(year_to)
    conn = get_db()
    assoc_id = request.args.get('association_id', type=int)
    aj, ac, ap = get_assoc_filter(conn, assoc_id)
    conditions = ac + conditions
    params     = ap + params
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    if group_by == 'species':
        q = f"SELECT g.species as label,SUM(g.count) as total FROM game_log g JOIN hunters h ON g.hunter_id=h.id {aj} {where} GROUP BY g.species ORDER BY total DESC"
    else:
        q = f"SELECT h.name as label,SUM(g.count) as total,h.id as hunter_id FROM game_log g JOIN hunters h ON g.hunter_id=h.id {aj} {where} GROUP BY g.hunter_id ORDER BY total DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/stats/species')
@login_required
def species_list():
    conn = get_db()
    assoc_id = request.args.get('association_id', type=int)
    aj, ac, ap = get_assoc_filter(conn, assoc_id)
    where = ("WHERE " + " AND ".join(ac)) if ac else ""
    q = f"SELECT DISTINCT g.species FROM game_log g JOIN hunters h ON g.hunter_id=h.id {aj} {where} ORDER BY g.species"
    rows = conn.execute(q, ap).fetchall()
    conn.close()
    return jsonify([r['species'] for r in rows])

@app.route('/api/stats/locations')
@login_required
def locations_list():
    conn = get_db()
    assoc_id = request.args.get('association_id', type=int)
    aj, ac, ap = get_assoc_filter(conn, assoc_id)
    conds = ["g.location != ''"] + ac
    where = "WHERE " + " AND ".join(conds)
    q = f"SELECT DISTINCT g.location FROM game_log g JOIN hunters h ON g.hunter_id=h.id {aj} {where} ORDER BY g.location"
    rows = conn.execute(q, ap).fetchall()
    conn.close()
    return jsonify([r['location'] for r in rows])


# ── Saved views ───────────────────────────────────────────

@app.route('/api/views', methods=['GET'])
@login_required
def get_views():
    conn = get_db()
    uid  = session.get('user_id')
    role = session.get('role')
    if role == 'admin':
        # Admins see everything
        rows = conn.execute('''
            SELECT sv.*, u.username as owner_username
            FROM saved_views sv LEFT JOIN users u ON sv.owner_id = u.id
            ORDER BY sv.owner_id, sv.name
        ''').fetchall()
    else:
        # Others see: all public views + their own private views
        rows = conn.execute('''
            SELECT sv.*, u.username as owner_username
            FROM saved_views sv LEFT JOIN users u ON sv.owner_id = u.id
            WHERE sv.is_private = 0 OR sv.owner_id = ?
            ORDER BY sv.owner_id, sv.name
        ''', (uid,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/views', methods=['POST'])
@login_required
def save_view():
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    is_private = 1 if data.get('is_private') else 0
    conn.execute("INSERT INTO saved_views (name,filters,chart_type,owner_id,is_private) VALUES(?,?,?,?,?)",
                 (data['name'], json.dumps(data.get('filters',{})), data.get('chart_type','bar'), session.get('user_id'), is_private))
    conn.commit()
    view = conn.execute("SELECT * FROM saved_views ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return jsonify(dict(view)), 201

@app.route('/api/views/<int:view_id>', methods=['PUT'])
@login_required
def update_view(view_id):
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    conn = get_db()
    view = conn.execute("SELECT * FROM saved_views WHERE id=?", (view_id,)).fetchone()
    if not view:
        conn.close()
        return jsonify({'error': 'View not found'}), 404
    if session.get('role') != 'admin' and view['owner_id'] != session.get('user_id'):
        conn.close()
        return jsonify({'error': 'You can only edit your own views'}), 403
    is_private = 1 if data.get('is_private') else 0
    conn.execute(
        "UPDATE saved_views SET name=?, filters=?, chart_type=?, is_private=? WHERE id=?",
        (data['name'], json.dumps(data.get('filters', {})), data.get('chart_type', 'bar'), is_private, view_id)
    )
    conn.commit()
    view = conn.execute("SELECT * FROM saved_views WHERE id=?", (view_id,)).fetchone()
    conn.close()
    return jsonify(dict(view))


@app.route('/api/views/<int:view_id>', methods=['DELETE'])
@login_required
def delete_view(view_id):
    conn = get_db()
    view = conn.execute("SELECT * FROM saved_views WHERE id=?", (view_id,)).fetchone()
    if not view:
        conn.close()
        return jsonify({'error': 'View not found'}), 404
    if session.get('role') != 'admin' and view['owner_id'] != session.get('user_id'):
        conn.close()
        return jsonify({'error': 'You can only delete your own views'}), 403
    conn.execute("DELETE FROM saved_views WHERE id=?", (view_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# ── Embed tokens ──────────────────────────────────────────

@app.route('/api/embed/tokens', methods=['GET'])
@admin_required
def get_tokens():
    conn = get_db()
    rows = conn.execute("SELECT * FROM embed_tokens ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/embed/tokens', methods=['POST'])
@admin_required
def create_token():
    data = request.json or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    view_id = data.get('view_id')
    if not view_id:
        return jsonify({'error': 'a saved view is required to create an embed'}), 400
    # Verify the view exists
    conn = get_db()
    vrow = conn.execute("SELECT id FROM saved_views WHERE id=?", (view_id,)).fetchone()
    if not vrow:
        conn.close()
        return jsonify({'error': 'saved view not found'}), 404
    token = secrets.token_urlsafe(24)
    conn.execute("INSERT INTO embed_tokens (token,name,mode,view_id,params) VALUES(?,?,?,?,?)",
                 (token, data['name'], 'leaderboard', view_id, '{}'))
    conn.commit()
    row = conn.execute("SELECT * FROM embed_tokens WHERE token=?", (token,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201

@app.route('/api/embed/tokens/<int:token_id>', methods=['DELETE'])
@admin_required
def delete_token(token_id):
    conn = get_db()
    conn.execute("DELETE FROM embed_tokens WHERE id=?", (token_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/embed/tokens/<int:token_id>/rotate', methods=['POST'])
@admin_required
def rotate_token(token_id):
    new_token = secrets.token_urlsafe(24)
    conn = get_db()
    conn.execute("UPDATE embed_tokens SET token=? WHERE id=?", (new_token, token_id))
    conn.commit()
    row = conn.execute("SELECT * FROM embed_tokens WHERE id=?", (token_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)) if row else (jsonify({'error': 'not found'}), 404)

def validate_embed_token(token):
    if not token:
        return None
    conn = get_db()
    row = conn.execute("SELECT * FROM embed_tokens WHERE token=?", (token,)).fetchone()
    if row:
        conn.execute("UPDATE embed_tokens SET last_used=datetime('now'),use_count=use_count+1 WHERE token=?", (token,))
        conn.commit()
    conn.close()
    return row

@app.route('/api/embed/data')
@cors_public
def embed_data():
    token = request.args.get('token')
    tok = validate_embed_token(token)
    if not tok:
        return jsonify({'error': 'invalid token'}), 403
    if not tok['view_id']:
        return jsonify({'error': 'embed token has no linked view'}), 400

    conn = get_db()
    vrow = conn.execute("SELECT * FROM saved_views WHERE id=?", (tok['view_id'],)).fetchone()
    conn.close()
    if not vrow:
        return jsonify({'error': 'linked view no longer exists'}), 404

    # View is the single source of truth — no overrides
    filters   = json.loads(vrow['filters'] or '{}')
    params    = {**filters, 'chart_type': vrow['chart_type'] or 'bar'}
    mode      = 'leaderboard'

    conditions, qparams = [], []
    if params.get('hunter_ids'):
        ids = params['hunter_ids']; conditions.append(f"g.hunter_id IN ({','.join('?'*len(ids))})"); qparams.extend(ids)
    if params.get('species'):
        sp = params['species']; conditions.append(f"g.species IN ({','.join('?'*len(sp))})"); qparams.extend(sp)
    if params.get('locations'):
        locs = params['locations']; conditions.append(f"g.location IN ({','.join('?'*len(locs))})"); qparams.extend(locs)
    if params.get('year_from'):
        conditions.append("strftime('%Y',g.hunt_date)>=?"); qparams.append(params['year_from'])
    if params.get('year_to'):
        conditions.append("strftime('%Y',g.hunt_date)<=?"); qparams.append(params['year_to'])
    where    = ("WHERE "+" AND ".join(conditions)) if conditions else ""
    group_by = params.get('group_by', 'hunter')
    if group_by == 'species':
        q = f"SELECT g.species as label,SUM(g.count) as total FROM game_log g JOIN hunters h ON g.hunter_id=h.id {where} GROUP BY g.species ORDER BY total DESC"
    else:
        q = f"SELECT h.name as label,SUM(g.count) as total,h.id as hunter_id FROM game_log g JOIN hunters h ON g.hunter_id=h.id {where} GROUP BY g.hunter_id ORDER BY total DESC"
    conn = get_db()
    lb   = [dict(r) for r in conn.execute(q, qparams).fetchall()]
    stats = {}
    if mode == 'dashboard':
        total_game = conn.execute("SELECT SUM(count) FROM game_log").fetchone()[0] or 0
        n_hunters  = conn.execute("SELECT COUNT(*) FROM hunters").fetchone()[0]
        n_species  = conn.execute("SELECT COUNT(DISTINCT species) FROM game_log").fetchone()[0]
        by_species = [dict(r) for r in conn.execute(
            "SELECT species as label,SUM(count) as total FROM game_log GROUP BY species ORDER BY total DESC"
        ).fetchall()]
        stats = {'total_game': total_game, 'n_hunters': n_hunters, 'n_species': n_species, 'by_species': by_species}
    conn.close()
    return jsonify({'mode': mode, 'params': params, 'token_name': tok['name'], 'leaderboard': lb, 'stats': stats})


# ── Entry point ───────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5050,
            debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')

"""
Class Artifacts starter web app ("One Module, One Activity").

Students log in, open an activity, fill it in, and get an artifact card to attach to the discussion post.
Each student sees only their own work. The instructor sees class results live and can export a CSV.

Run locally:
    pip install -r requirements.txt
    python app.py load-roster roster_sample.csv
    python app.py                      # http://localhost:5000

Activities are defined in course.py. Data is stored in SQLite (data/app.db) unless DATABASE_PATH is set.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from functools import wraps

from flask import (Flask, Response, abort, flash, g, redirect, render_template, request, session,
                   url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import course

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "data", "app.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT UNIQUE NOT NULL,
    pw_hash    TEXT NOT NULL,
    name       TEXT NOT NULL DEFAULT '',
    is_admin   INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS submissions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL,
    activity    TEXT NOT NULL,
    data        TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    UNIQUE (student_id, activity)
);
CREATE TABLE IF NOT EXISTS settings (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);
"""

ACTIVITIES = sorted(course.ACTIVITIES, key=lambda a: (a["module"], a["slug"]))
BY_SLUG = {a["slug"]: a for a in ACTIVITIES}


# ---------- database ----------

def get_db() -> sqlite3.Connection:
    if "db" not in g:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db() -> None:
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def load_roster(text: str) -> tuple[int, int]:
    """Roster CSV columns: username,password,name,is_admin. Existing usernames are updated."""
    db = get_db()
    added = updated = 0
    for row in csv.DictReader(io.StringIO(text)):
        username = (row.get("username") or "").strip().lower()
        password = (row.get("password") or "").strip()
        if not username or not password:
            continue
        values = (generate_password_hash(password), (row.get("name") or "").strip(),
                  1 if (row.get("is_admin") or "").strip() in ("1", "yes", "true") else 0)
        if db.execute("SELECT 1 FROM students WHERE username = ?", (username,)).fetchone():
            db.execute("UPDATE students SET pw_hash = ?, name = ?, is_admin = ? WHERE username = ?", (*values, username))
            updated += 1
        else:
            db.execute("INSERT INTO students (pw_hash, name, is_admin, username) VALUES (?,?,?,?)", (*values, username))
            added += 1
    db.commit()
    return added, updated


def is_open(slug: str) -> bool:
    row = get_db().execute("SELECT value FROM settings WHERE key = ?", (f"open:{slug}",)).fetchone()
    return row is None or row["value"] == "1"


# ---------- helpers ----------

def variant_for(username: str, activity: dict) -> tuple[str, str] | None:
    """Same student, same activity -> same input, every time. Returns (label, text)."""
    variants = activity.get("variants") or []
    if not variants:
        return None
    n = int(hashlib.sha256(f"{username}:{activity['slug']}".encode()).hexdigest(), 16) % len(variants)
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[n % 26], variants[n]


def read_form(activity: dict) -> dict:
    data = {}
    for f in activity["fields"]:
        if f["type"] == "checks":
            data[f["name"]] = [v for v in request.form.getlist(f["name"]) if v in f["options"]]
        elif f["type"] == "choice":
            v = request.form.get(f["name"], "")
            data[f["name"]] = v if v in f["options"] else ""
        else:
            data[f["name"]] = request.form.get(f["name"], "").strip()[:2000]
    return data


def as_text(value) -> str:
    return ", ".join(value) if isinstance(value, list) else (value or "")


def current_user():
    uid = session.get("uid")
    if uid is None:
        return None
    return get_db().execute("SELECT * FROM students WHERE id = ?", (uid,)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("login", next=request.path))
        if not user["is_admin"]:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


# ---------- app ----------

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        init_db()

    @app.context_processor
    def inject():
        return {"course_name": course.COURSE_NAME, "user": current_user()}

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip().lower()
            row = get_db().execute("SELECT * FROM students WHERE username = ?", (username,)).fetchone()
            if row and check_password_hash(row["pw_hash"], request.form.get("password", "")):
                session.clear()
                session["uid"] = row["id"]
                nxt = request.args.get("next", "")
                return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else url_for("home"))
            flash("That username and password do not match the roster.")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def home():
        uid = current_user()["id"]
        done = {r["activity"] for r in get_db().execute("SELECT activity FROM submissions WHERE student_id = ?", (uid,))}
        items = [(a, a["slug"] in done, is_open(a["slug"])) for a in ACTIVITIES]
        return render_template("home.html", items=items)

    @app.route("/a/<slug>", methods=["GET", "POST"])
    @login_required
    def activity(slug):
        act = BY_SLUG.get(slug) or abort(404)
        user = current_user()
        db = get_db()
        if request.method == "POST":
            if not is_open(slug):
                flash("This activity is closed.")
                return redirect(url_for("activity", slug=slug))
            data = read_form(act)
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            db.execute("""INSERT INTO submissions (student_id, activity, data, updated_at) VALUES (?,?,?,?)
                          ON CONFLICT(student_id, activity) DO UPDATE SET data = excluded.data,
                          updated_at = excluded.updated_at""", (user["id"], slug, json.dumps(data), now))
            db.commit()
            return redirect(url_for("activity", slug=slug, saved=1) + "#artifact")
        row = db.execute("SELECT * FROM submissions WHERE student_id = ? AND activity = ?", (user["id"], slug)).fetchone()
        data = json.loads(row["data"]) if row else {}
        return render_template("activity.html", act=act, data=data, row=row, open=is_open(slug),
                               variant=variant_for(user["username"], act), as_text=as_text,
                               saved=request.args.get("saved"))

    @app.route("/a/<slug>/artifact.txt")
    @login_required
    def artifact_txt(slug):
        act = BY_SLUG.get(slug) or abort(404)
        user = current_user()
        row = get_db().execute("SELECT * FROM submissions WHERE student_id = ? AND activity = ?",
                               (user["id"], slug)).fetchone() or abort(404)
        data = json.loads(row["data"])
        lines = [f"{course.COURSE_NAME}", f"Module {act['module']}: {act['title']}", f"For {act['discussion']}",
                 f"Student: {user['name'] or user['username']}", ""]
        v = variant_for(user["username"], act)
        if v:
            lines += [f"My input (version {v[0]}): {v[1]}", ""]
        for f in act["fields"]:
            lines += [f["label"], as_text(data.get(f["name"])), ""]
        return Response("\n".join(lines), mimetype="text/plain",
                        headers={"Content-Disposition": f"attachment; filename=artifact-{slug}.txt"})

    # ----- instructor -----

    @app.route("/admin/")
    @admin_required
    def admin_home():
        db = get_db()
        n_students = db.execute("SELECT COUNT(*) FROM students WHERE is_admin = 0").fetchone()[0]
        counts = dict(db.execute("SELECT activity, COUNT(*) FROM submissions GROUP BY activity").fetchall())
        items = [(a, counts.get(a["slug"], 0), is_open(a["slug"])) for a in ACTIVITIES]
        return render_template("admin_home.html", items=items, n_students=n_students)

    @app.route("/admin/<slug>/")
    @admin_required
    def admin_activity(slug):
        act = BY_SLUG.get(slug) or abort(404)
        rows = get_db().execute("""SELECT s.*, st.username, st.name FROM submissions s
                                   JOIN students st ON st.id = s.student_id
                                   WHERE s.activity = ? ORDER BY s.updated_at DESC""", (slug,)).fetchall()
        subs = [(r, json.loads(r["data"])) for r in rows]
        charts = []
        for f in act["fields"]:
            if f["type"] in ("choice", "checks"):
                c = Counter()
                for _, d in subs:
                    v = d.get(f["name"])
                    c.update(v if isinstance(v, list) else ([v] if v else []))
                charts.append((f, [(o, c.get(o, 0)) for o in f["options"]], max(c.values(), default=0)))
        return render_template("admin_activity.html", act=act, subs=subs, charts=charts, open=is_open(slug),
                               as_text=as_text)

    @app.route("/admin/<slug>/toggle", methods=["POST"])
    @admin_required
    def admin_toggle(slug):
        BY_SLUG.get(slug) or abort(404)
        db = get_db()
        db.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                   (f"open:{slug}", "0" if is_open(slug) else "1"))
        db.commit()
        return redirect(request.referrer or url_for("admin_home"))

    @app.route("/admin/<slug>/export.csv")
    @admin_required
    def admin_export(slug):
        act = BY_SLUG.get(slug) or abort(404)
        rows = get_db().execute("""SELECT s.*, st.username, st.name FROM submissions s
                                   JOIN students st ON st.id = s.student_id WHERE s.activity = ?""", (slug,)).fetchall()
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["username", "name", "updated_at", "version"] + [f["name"] for f in act["fields"]])
        for r in rows:
            d = json.loads(r["data"])
            v = variant_for(r["username"], act)
            w.writerow([r["username"], r["name"], r["updated_at"], v[0] if v else ""] +
                       [as_text(d.get(f["name"])) for f in act["fields"]])
        return Response(out.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment; filename={slug}.csv"})

    @app.route("/admin/roster", methods=["GET", "POST"])
    @admin_required
    def admin_roster():
        if request.method == "POST" and request.files.get("roster"):
            added, updated = load_roster(request.files["roster"].read().decode("utf-8-sig"))
            flash(f"Roster loaded: {added} added, {updated} updated.")
        students = get_db().execute("SELECT username, name, is_admin FROM students ORDER BY is_admin DESC, name").fetchall()
        return render_template("admin_roster.html", students=students)

    return app


app = create_app()

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "load-roster":
        with app.app_context():
            with open(sys.argv[2], encoding="utf-8-sig") as fh:
                print("roster: %d added, %d updated" % load_roster(fh.read()))
    else:
        app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)

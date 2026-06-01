# scan-for-injection / scan-for-ssrf / scan-broken-access-control fixture (Python)
# Intentionally vulnerable — do not deploy

import subprocess
import sqlite3
import urllib.request
import ipaddress
import socket
from urllib.parse import urlparse
import re
from flask import Flask, request, jsonify, abort

app = Flask(__name__)


# Lightweight dummy DB for linting and local testing (fixture only)
class _DummyDB:
    def get_invoice(self, invoice_id):
        return {}

    def update_user(self, *args, **kwargs):
        return None

    def get_all_users(self):
        return []


db = _DummyDB()


def _get_int_arg(name: str):
    try:
        return int(request.args.get(name, ""))
    except Exception:
        return None


# SI-001: Use parameterized query to avoid SQL injection
@app.route("/user")
def get_user():
    user_id = _get_int_arg("id")
    if user_id is None:
        abort(400, "invalid id")
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    return jsonify(row or {})


def _valid_hostname(host: str) -> bool:
    if not host or len(host) > 253:
        return False
    # allow letters, digits, dot, and hyphen
    if not re.match(r"^[A-Za-z0-9.-]+$", host):
        return False
    if ".." in host:
        return False
    return True


# SI-002: use subprocess without shell and validate host
@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    if not _valid_hostname(host):
        abort(400, "invalid host")
    # cross-platform ping; prefer no shell usage
    cmd = ["ping", "-c", "1", host]
    if socket.gethostname().lower().endswith("windows") or False:
        cmd = ["ping", "-n", "1", host]
    try:
        proc = subprocess.run(cmd, capture_output=True, check=True, text=True, timeout=5)
        return proc.stdout
    except subprocess.SubprocessError:
        abort(502, "ping failed")


# SI-003: do not execute user-supplied code; return an error
@app.route("/eval")
def run_code():
    return ("Execution of user-supplied code is disabled in safe mode.", 403)


def _escape_ldap(s: str) -> str:
    if s is None:
        return ""
    # escape special LDAP filter characters
    return re.sub(r"([\\*()\x00])", lambda m: "\\" + m.group(1), s)


@app.route("/ldap-search")
def ldap_search():
    username = request.args.get("user", "")
    safe_user = _escape_ldap(username)
    ldap_filter = f"(&(uid={safe_user})(objectClass=person))"
    return ldap_filter


def _is_private_netloc(netloc: str) -> bool:
    if not netloc:
        return True
    host = netloc.split(":")[0]
    # direct IP check
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback
    except Exception:
        # treat hostnames containing localhost or numeric private patterns as private
        if "localhost" in host or host.startswith("127."):
            return True
        return False


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or _is_private_netloc(parsed.netloc):
        abort(400, "invalid or disallowed url")
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = resp.read()
        return data
    except Exception:
        abort(502, "fetch failed")


@app.route("/proxy")
def proxy():
    target = request.args.get("target", "")
    parsed = urlparse(target)
    if parsed.scheme not in ("http", "https") or _is_private_netloc(parsed.netloc):
        abort(400, "invalid or disallowed target")
    import requests

    try:
        resp = requests.get(target, allow_redirects=False, timeout=5)
        return resp.content
    except Exception:
        abort(502, "proxy failed")


# BAC-001: Broken object-level authorization — no ownership check
@app.route("/invoice/<int:invoice_id>")
def get_invoice(invoice_id):
    # Require an X-User-Id header and verify ownership (fixture-only simple check)
    header_user = request.headers.get("X-User-Id")
    try:
        header_user_id = int(header_user) if header_user is not None else None
    except Exception:
        header_user_id = None
    if header_user_id is None or header_user_id != invoice_id:
        abort(403, "forbidden")
    return jsonify(db.get_invoice(invoice_id))


# BAC-002: Mass assignment — all fields accepted from client
@app.route("/profile", methods=["POST"])
def update_profile():
    data = request.get_json() or {}
    # Prevent mass-assignment: whitelist allowed fields
    allowed = {"name", "email", "bio"}
    safe_data = {k: v for k, v in data.items() if k in allowed}
    header_user = request.headers.get("X-User-Id")
    try:
        header_user_id = int(header_user) if header_user is not None else None
    except Exception:
        header_user_id = None
    if header_user_id is None:
        abort(403, "authentication required")
    db.update_user(header_user_id, **safe_data)
    return jsonify({"ok": True})


# BAC-003: Forced browsing — admin endpoint with no auth check
@app.route("/admin/export-users")
def export_users():
    # Require admin header for fixture
    is_admin = request.headers.get("X-Admin")
    if is_admin != "1":
        abort(403, "admin required")
    return jsonify(db.get_all_users())


if __name__ == "__main__":
    # Do not enable debug or wildcard bind in safe-mode by default
    app.run(debug=False, host="127.0.0.1")

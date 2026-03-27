# =========================
# ENVIRONMENT SETUP (FIXED)
# =========================
from utils.env_check import load_environment, validate_required_vars

# Load environment variables (local + cloud compatible)
load_environment()

# Validate required variables (add critical ones later)
validate_required_vars([
    # "APP_KEY",
    # "DATABASE_URL",
])

# =========================
# ORIGINAL FILE CONTINUES
# =========================

import os
import re
import sys

# Print startup banner EARLY
if __name__ == "__main__":
    from utils.version import get_version as _get_version_early

    _host_ip = os.getenv("FLASK_HOST_IP", "127.0.0.1")
    _port = int(os.getenv("FLASK_PORT", 5000))
    _ws_port = int(os.getenv("WEBSOCKET_PORT", 8765))
    _debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    _is_reloader_parent = _debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true"

    if not _is_reloader_parent:
        _display_ip = _host_ip
        if _host_ip == "0.0.0.0":
            import socket as _sock
            try:
                _s = _sock.socket(_sock.AF_INET, _sock.SOCK_DGRAM)
                _s.connect(("8.8.8.8", 80))
                _display_ip = _s.getsockname()[0]
                _s.close()
            except Exception:
                _display_ip = "127.0.0.1"

        _version = _get_version_early()
        _web_url = f"http://{_display_ip}:{_port}"
        _ws_url = f"ws://{_display_ip}:{_ws_port}"
        _docs_url = "https://docs.openalgo.in"

        print(f"\n🚀 OpenAlgo v{_version}")
        print(f"Web: {_web_url}")
        print(f"WS: {_ws_url}")
        print(f"Docs: {_docs_url}\n")

# ---- Rest of your original imports ----
import mimetypes
mimetypes.add_type("application/javascript", ".js")

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect

from extensions import socketio
from limiter import limiter

# (All your blueprint imports remain unchanged)
# Skipping here for brevity — keep exactly as your original file

# =========================
# CREATE APP
# =========================
def create_app():
    app = Flask(__name__)

    socketio.init_app(app)

    csrf = CSRFProtect(app)
    app.csrf = csrf

    limiter.init_app(app)

    # =========================
    # ENV VARIABLES USAGE
    # =========================
    app.secret_key = os.getenv("APP_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    if not app.secret_key:
        print("⚠️ WARNING: APP_KEY not set")

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        print("⚠️ WARNING: DATABASE_URL not set")

    # =========================
    # BASIC CONFIG
    # =========================
    HOST_SERVER = os.getenv("HOST_SERVER", "http://127.0.0.1:5000")
    USE_HTTPS = HOST_SERVER.startswith("https://")

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=USE_HTTPS,
    )

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    # Keep all your blueprint registrations here exactly as-is

    return app

@app.route("/")
def home():
    return {
        "status": "running",
        "app": "OpenAlgo",
        "mode": "local" if __name__ == "__main__" else "cloud"
    }
# =========================
# INIT APP
# =========================
app = create_app()

# =========================
# SOCKET / SERVER START
# =========================
if __name__ == "__main__":
    host_ip = os.getenv("FLASK_HOST_IP", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

    # Disable ngrok in cloud
    if os.getenv("ENV") != "PROD":
        if os.getenv("NGROK_ALLOW", "FALSE").upper() == "TRUE":
            from utils.ngrok_manager import start_ngrok_tunnel
            start_ngrok_tunnel(port)

    socketio.run(
        app,
        host=host_ip,
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )
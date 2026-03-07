"""
Flask Frontend Server
Run with: python flask_app.py
Open:     http://localhost:5000
"""

import os
import shutil
from flask import Flask, render_template, request, jsonify
import requests

# ── Bulletproof path setup for Windows ──────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# Auto-create templates folder if missing
if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)
    print(f"  📁 Created folder: {TEMPLATE_DIR}")

# Auto-move index.html from root into templates if needed
root_html     = os.path.join(BASE_DIR, "index.html")
template_html = os.path.join(TEMPLATE_DIR, "index.html")

if os.path.exists(root_html) and not os.path.exists(template_html):
    shutil.copy(root_html, template_html)
    print(f"  ✅ Copied index.html → templates/index.html automatically")

# Print debug info so you can confirm the path
print(f"\n  📂 Template folder : {TEMPLATE_DIR}")
print(f"  📄 index.html found: {os.path.exists(template_html)}\n")

# ── Flask app ────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder=TEMPLATE_DIR)

FASTAPI_URL = "http://localhost:8000"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json(force=True)
        resp = requests.post(f"{FASTAPI_URL}/translate", json=data, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"detail": "Cannot reach FastAPI. Make sure fastapi_server.py is running on port 8000."}), 503
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@app.route("/api/detect", methods=["POST"])
def detect():
    try:
        data = request.get_json(force=True)
        resp = requests.post(f"{FASTAPI_URL}/detect", json=data, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"detail": "Cannot reach FastAPI. Make sure fastapi_server.py is running."}), 503
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@app.route("/api/languages")
def languages():
    try:
        resp = requests.get(f"{FASTAPI_URL}/languages", timeout=5)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"detail": "Cannot reach FastAPI. Make sure fastapi_server.py is running."}), 503
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


if __name__ == "__main__":
    print("  🌐  Flask frontend: http://localhost:5000")
    print("  ⚡  FastAPI must be running on port 8000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)

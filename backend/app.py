from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import subprocess
import platform
import time

app = Flask(__name__)
CORS(app)

DATABASE = "database.db"


# ==============================
# Database Connection
# ==============================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================
# Create Database
# ==============================

def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip TEXT NOT NULL,
            device_type TEXT NOT NULL,
            status TEXT DEFAULT 'Offline',
            response_time INTEGER
        )
    """)

    conn.commit()
    conn.close()


# ==============================
# Ping Device
# ==============================

def ping_device(ip):

    if platform.system() == "Windows":

        command = [
            "ping",
            "-n",
            "1",
            "-w",
            "1000",
            ip
        ]

    else:

        command = [
            "ping",
            "-c",
            "1",
            "-W",
            "1",
            ip
        ]

    start_time = time.time()

    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    end_time = time.time()

    response_time = round(
        (end_time - start_time) * 1000
    )

    if result.returncode == 0:

        return "Online", response_time

    else:

        return "Offline", None


# ==============================
# Home
# ==============================

@app.route("/")
def home():

    return jsonify({
        "message": "Network Dashboard API is running"
    })


# ==============================
# Get Devices
# ==============================

@app.route("/api/devices", methods=["GET"])
def get_devices():

    conn = get_db()

    devices = conn.execute(
        "SELECT * FROM devices"
    ).fetchall()

    conn.close()

    return jsonify([
        dict(device)
        for device in devices
    ])


# ==============================
# Add Device
# ==============================

@app.route("/api/devices", methods=["POST"])
def add_device():

    data = request.json

    name = data.get("name")
    ip = data.get("ip")
    device_type = data.get("device_type")

    if not name or not ip or not device_type:

        return jsonify({
            "error": "All fields are required"
        }), 400


    # Ping the IP address

    status, response_time = ping_device(ip)


    # Save to database

    conn = get_db()

    conn.execute("""
        INSERT INTO devices
        (name, ip, device_type, status, response_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        ip,
        device_type,
        status,
        response_time
    ))

    conn.commit()
    conn.close()


    return jsonify({
        "message": "Device added successfully",
        "status": status,
        "response_time": response_time
    }), 201


# ==============================
# Delete Device
# ==============================

@app.route(
    "/api/devices/<int:device_id>",
    methods=["DELETE"]
)
def delete_device(device_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM devices WHERE id = ?",
        (device_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Device deleted"
    })


# ==============================
# Start Application
# ==============================

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
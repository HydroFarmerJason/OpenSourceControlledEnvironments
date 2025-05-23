#!/usr/bin/env python3
"""
Container Farm Control System - REST API
This lightweight API exposes sensor readings and simple
control commands from the local system. It is intended
as a foundation for mobile apps or third party services.
"""

from flask import Flask, jsonify, request
import json
import os
import time
from datetime import datetime
from middleware.auth import require_api_key

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "user_choices.json")

# Paths for student management and activity logging
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
STUDENTS_FILE = os.path.join(BASE_DIR, "config", "students.json")
LOG_DIR = os.path.join(BASE_DIR, "logs", "student_logs")
ACTIVITY_FILE = os.path.join(LOG_DIR, "activities.json")


def load_data():
    """Load sensor data from a JSON file (placeholder)."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def load_students():
    """Load registered students."""
    if not os.path.exists(STUDENTS_FILE):
        return {"students": []}
    with open(STUDENTS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"students": []}


def save_students(data):
    """Save students to file."""
    os.makedirs(os.path.dirname(STUDENTS_FILE), exist_ok=True)
    with open(STUDENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_activity(student, action, details=""):
    """Append a student activity to the log."""
    os.makedirs(LOG_DIR, exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "student": student,
        "action": action,
        "details": details,
    }
    activities = []
    if os.path.exists(ACTIVITY_FILE):
        try:
            with open(ACTIVITY_FILE, "r") as f:
                activities = json.load(f)
        except json.JSONDecodeError:
            activities = []
    activities.append(log_entry)
    with open(ACTIVITY_FILE, "w") as f:
        json.dump(activities, f, indent=2)
    return log_entry


@app.route("/api/status", methods=["GET"])
@require_api_key
def status():
    """Return basic system status."""
    data = load_data()
    return jsonify({"status": "ok", "data": data})


@app.route("/api/control/<string:output>", methods=["POST"])
@require_api_key
def control(output):
    """Placeholder route to toggle an output."""
    action = request.json.get("action", "toggle")
    # This is only a placeholder; real implementation would
    # interface with Mycodo or GPIO to control hardware.
    return jsonify({"output": output, "action": action, "success": True})


@app.route("/api/students", methods=["GET"])
@require_api_key
def list_students():
    """Return all registered students."""
    data = load_students()
    return jsonify(data)


@app.route("/api/students", methods=["POST"])
@require_api_key
def add_student():
    """Add a new student."""
    payload = request.get_json(force=True)
    name = payload.get("name")
    if not name:
        return jsonify({"error": "name required"}), 400
    grade = payload.get("grade")
    sid = payload.get("id")
    data = load_students()
    data.setdefault("students", [])
    for stu in data["students"]:
        if stu["name"].lower() == name.lower():
            return jsonify({"error": "student exists"}), 409
    new_student = {
        "name": name,
        "grade": grade,
        "id": sid or str(int(time.time())),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data["students"].append(new_student)
    save_students(data)
    return jsonify({"success": True, "student": new_student})


@app.route("/api/activities", methods=["POST"])
@require_api_key
def add_activity():
    """Log a student activity."""
    payload = request.get_json(force=True)
    student = payload.get("student")
    action = payload.get("action")
    details = payload.get("details", "")
    if not student or not action:
        return jsonify({"error": "student and action required"}), 400
    entry = log_activity(student, action, details)
    return jsonify({"success": True, "entry": entry})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

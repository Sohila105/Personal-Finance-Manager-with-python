# data_manager.py
# Centralized file I/O and backups for JSON datasets.

import json
import os
from datetime import datetime
from shutil import copyfile

# -------------------------------
# Default file paths
# -------------------------------
DATA_DIR = "data"
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

FILES = {
    "users": os.path.join(DATA_DIR, "users.json"),
    "transactions": os.path.join(DATA_DIR, "transactions.json"),
    "goals": os.path.join(DATA_DIR, "goals.json"),
    "budgets": os.path.join(DATA_DIR, "budgets.json"),
    "reminders": os.path.join(DATA_DIR, "reminders.json"),
}

def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

_ensure_dirs()

# -------------------------------
# Core JSON helpers
# -------------------------------
def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# -------------------------------
# Backups
# -------------------------------
def backup_file(path):
    if not os.path.exists(path):
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.basename(path)
    dest = os.path.join(BACKUP_DIR, f"{base}_{ts}.bak")
    try:
        copyfile(path, dest)
        print(f"Backup created: {os.path.basename(dest)}")
    except Exception as e:
        print(f"Backup failed for {path}: {e}")

# -------------------------------
# Unified save/load
# -------------------------------
def load_all():
    return {k: load_json(p) for k, p in FILES.items()}

def save_all(datasets: dict):
    for k, p in FILES.items():
        if k in datasets:
            backup_file(p)
            save_json(p, datasets[k])

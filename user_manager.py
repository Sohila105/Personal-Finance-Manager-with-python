# user_manager.py
# User operations backed by data_manager.

from datetime import datetime
from typing import Optional, List
import hashlib
import getpass


from data_manager import load_json, save_json, FILES
from utils import get_nonempty_input
import ui

USERS_PATH = FILES["users"]

# Module-level state
_users: List[dict] = load_json(USERS_PATH)
_current_user: Optional[dict] = None

# password hashing
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- Queries ----------
def find_user(username: str):
    username = (username or "").strip()
    for u in _users:
        if u.get("username") == username:
            return u
    return None

def get_current_user():
    return _current_user

def is_logged_in() -> bool:
    return _current_user is not None

def get_users_data() -> List[dict]:
    return _users

# ---------- Core ops ----------
def register_user():
    global _users
    ui.section("Register New User")
    username = get_nonempty_input("Enter a username: ")
    if find_user(username):
        ui.status_err("Username already exists. Try another one.")
        return

    password = getpass.getpass("Enter a password (numbers only for simplicity): ")
    hashed_pw = hash_password(password)
    currency = input("Preferred currency (e.g., USD, EGP, EUR): ").upper().strip() or "USD"

    new_user = {
        "username": username,
        "password": hashed_pw,
        "currency": currency,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    _users.append(new_user)
    save_json(USERS_PATH, _users)
    ui.status_ok(f"User '{username}' registered successfully!")

def login_user():
    global _current_user
    ui.section("Login")
    username = get_nonempty_input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    user = find_user(username)
    if user and user.get("password") == hash_password(password):
        _current_user = user
        ui.status_ok(f"Welcome back, {username}!")
    else:
        ui.status_err("Invalid username or password.")

def logout_user():
    global _current_user
    if _current_user:
        ui.status_ok(f"Logged out from {_current_user['username']}.")
        _current_user = None
    else:
        ui.status_warn("No user is currently logged in.")

# ---------- Save/Reload ----------
def reload_users():
    global _users
    _users = load_json(USERS_PATH)

def save_users():
    save_json(USERS_PATH, _users)

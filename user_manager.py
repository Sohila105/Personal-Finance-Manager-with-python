# User operations backed by data_manager.

from datetime import datetime
from typing import Optional, List

from data_manager import load_json, save_json, FILES
from utils import get_nonempty_input

USERS_PATH = FILES["users"]

# Module-level state
_users: List[dict] = load_json(USERS_PATH)
_current_user: Optional[dict] = None

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
    print("\n--- Register New User ---")
    username = get_nonempty_input("Enter a username: ")
    if find_user(username):
        print("Username already exists. Try another one.")
        return

    password = get_nonempty_input("Enter a password (numbers only for simplicity): ")
    currency = input("Preferred currency (e.g., USD, EGP, EUR): ").upper().strip() or "USD"

    new_user = {
        "username": username,
        "password": password,
        "currency": currency,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    _users.append(new_user)
    save_json(USERS_PATH, _users)
    print(f"User '{username}' registered successfully!")

def login_user():
    global _current_user
    print("\n--- Login ---")
    username = get_nonempty_input("Enter username: ")
    password = get_nonempty_input("Enter password: ")

    user = find_user(username)
    if user and user.get("password") == password:
        _current_user = user
        print(f"Welcome back, {username}!")
    else:
        print("Invalid username or password.")

def logout_user():
    global _current_user
    if _current_user:
        print(f"Logged out from {_current_user['username']}.")
        _current_user = None
    else:
        print("No user is currently logged in.")

# ---------- Save/Reload ----------
def reload_users():
    global _users
    _users = load_json(USERS_PATH)

def save_users():
    save_json(USERS_PATH, _users)

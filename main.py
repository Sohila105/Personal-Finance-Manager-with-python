# Setup and Data Handling
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal

# File paths for data storage
USERS_FILE = "users.json"
TRANSACTIONS_FILE = "transactions.json"
GOALS_FILE = "goals.json"
BUDGET_FILE = "budgets.json"
REMINDERS_FILE = "reminders.json"


# Load and Save Functions
def load_data(file_path):
    """Load data from a JSON file, return empty list if file not found."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_data(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


# Initialize global data
users = load_data(USERS_FILE)
transactions = load_data(TRANSACTIONS_FILE)
goals = load_data(GOALS_FILE)
budgets = load_data(BUDGET_FILE)
reminders = load_data(REMINDERS_FILE)

# Keep track of the currently logged-in user
current_user = None


# Helper Functions
def find_user(username):
    """Find a user by username."""
    for user in users:
        if user["username"] == username:
            return user
    return None

def save_all():
    """Save all data files at once."""
    save_data(USERS_FILE, users)
    save_data(TRANSACTIONS_FILE, transactions)
    save_data(GOALS_FILE, goals)
    save_data(BUDGET_FILE, budgets)
    save_data(REMINDERS_FILE, reminders)

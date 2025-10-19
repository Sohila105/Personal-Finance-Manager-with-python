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



#User System (Register, Login, Logout)
def register_user():
    """Register a new user with username, password, and currency."""
    print("\n--- Register New User ---")
    username = input("Enter a username: ").strip()
    if find_user(username):
        print("Username already exists. Try another one.")
        return

    password = input("Enter a password (numbers only for simplicity): ").strip()
    currency = input("Preferred currency (e.g., USD, EGP, EUR): ").upper().strip()

    new_user = {
        "username": username,
        "password": password,
        "currency": currency
    }

    users.append(new_user)
    save_data(USERS_FILE, users)
    print(f"User '{username}' registered successfully!")


def login_user():
    """Login existing user."""
    global current_user
    print("\n--- Login ---")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    user = find_user(username)
    if user and user["password"] == password:
        current_user = user
        print(f"Welcome back, {username}!")
    else:
        print("Invalid username or password.")


def logout_user():
    """Logout the current user."""
    global current_user
    if current_user:
        print(f"Logged out from {current_user['username']}.")
        current_user = None
    else:
        print("No user is currently logged in.")

#Transactions (Add, View, Edit, Delete)
def add_transaction():
    """Add a new income or expense transaction for the logged-in user."""
    if not current_user:
        print("Please log in first.")
        return

    print("\n--- Add Transaction ---")
    t_type = input("Type (income/expense): ").lower().strip()
    if t_type not in ["income", "expense"]:
        print("Invalid type.")
        return

    try:
        amount = Decimal(input("Amount: "))
    except:
        print("Invalid amount.")
        return

    category = input("Category (e.g. Food, Salary, Bills): ").title().strip()
    description = input("Description: ").strip()
    date = input("Date (YYYY-MM-DD, leave empty for today): ").strip()
    if date == "":
        date = datetime.today().strftime("%Y-%m-%d")

    new_id = len(transactions) + 1
    new_transaction = {
        "id": new_id,
        "username": current_user["username"],
        "type": t_type,
        "amount": float(amount),
        "category": category,
        "date": date,
        "description": description
    }

    transactions.append(new_transaction)
    save_data(TRANSACTIONS_FILE, transactions)
    print("Transaction added successfully!")


def view_transactions():
    """Display all transactions for the current user."""
    if not current_user:
        print("Please log in first.")
        return

    print(f"\n--- {current_user['username']}'s Transactions ---")
    user_txns = [t for t in transactions if t["username"] == current_user["username"]]

    if not user_txns:
        print("No transactions found.")
        return

    print(f"{'ID':<5}{'TYPE':<10}{'AMOUNT':<10}{'CATEGORY':<15}{'DATE':<12}{'DESC'}")
    print("-" * 65)
    for t in user_txns:
        print(f"{t['id']:<5}{t['type']:<10}{t['amount']:<10}{t['category']:<15}{t['date']:<12}{t['description']}")
    print("-" * 65)


def edit_transaction():
    """Edit an existing transaction."""
    if not current_user:
        print("Please log in first.")
        return

    view_transactions()
    try:
        txn_id = int(input("Enter the transaction ID to edit: "))
    except:
        print("Invalid ID.")
        return

    for t in transactions:
        if t["id"] == txn_id and t["username"] == current_user["username"]:
            print("Leave a field blank to keep it unchanged.")
            new_type = input(f"New type ({t['type']}): ").strip().lower() or t["type"]
            new_amount = input(f"New amount ({t['amount']}): ").strip()
            if new_amount:
                try:
                    t["amount"] = float(Decimal(new_amount))
                except:
                    print("Invalid amount. Keeping old value.")
            new_category = input(f"New category ({t['category']}): ").strip() or t["category"]
            new_desc = input(f"New description ({t['description']}): ").strip() or t["description"]

            t["type"] = new_type
            t["category"] = new_category
            t["description"] = new_desc

            save_data(TRANSACTIONS_FILE, transactions)
            print("Transaction updated successfully!")
            return
    print("Transaction not found.")


def delete_transaction():
    """Delete a transaction with confirmation."""
    if not current_user:
        print("Please log in first.")
        return

    view_transactions()
    try:
        txn_id = int(input("Enter the transaction ID to delete: "))
    except:
        print("Invalid ID.")
        return

    for t in transactions:
        if t["id"] == txn_id and t["username"] == current_user["username"]:
            confirm = input("Are you sure you want to delete this? (y/n): ").lower()
            if confirm == "y":
                transactions.remove(t)
                save_data(TRANSACTIONS_FILE, transactions)
                print("Transaction deleted.")
            else:
                print("Deletion cancelled.")
            return
    print("Transaction not found.")


#Main Menu
def main_menu():
    while True:
        print("\n========== Personal Finance Manager ==========")
        if current_user:
            print(f"Logged in as: {current_user['username']} ({current_user['currency']})")
        else:
            print("Not logged in")

        print("\n1. Register New User")
        print("2. Login")
        print("3. Logout")
        print("4. Exit")
        print("==============================================")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            login_user()
        elif choice == "3":
            logout_user()
        elif choice == "4":
            print("Saving data and exiting... Goodbye!")
            save_all()
            break
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main_menu()

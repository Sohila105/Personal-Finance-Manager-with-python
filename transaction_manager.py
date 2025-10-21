# transaction_manager.py
# Transactions backed by data_manager and session from user_manager.

from datetime import datetime, date
from decimal import Decimal
from typing import List

from data_manager import load_json, save_json, FILES
from utils import today_iso, get_number
import user_manager as um

TXNS_PATH = FILES["transactions"]

# Module-level state
_transactions: List[dict] = load_json(TXNS_PATH)

# ---------- Persistence ----------
def reload_transactions():
    global _transactions
    _transactions = load_json(TXNS_PATH)

def save_transactions():
    save_json(TXNS_PATH, _transactions)

# ---------- Utilities ----------
def _next_id_for_user(username: str) -> int:
    ids = [t["id"] for t in _transactions if t.get("username") == username]
    return (max(ids) + 1) if ids else 1

def _user_transactions(username: str) -> List[dict]:
    return [t for t in _transactions if t.get("username") == username]

def get_transactions_data() -> List[dict]:
    return _transactions

# ---------- Core ops ----------
def add_transaction():
    if not um.is_logged_in():
        print("Please log in first.")
        return

    user = um.get_current_user()
    print("\n--- Add Transaction ---")
    t_type = input("Type (income/expense): ").lower().strip()
    if t_type not in ("income", "expense"):
        print("Invalid type.")
        return

    amount = get_number("Amount: ")
    category = input("Category (e.g. Food, Salary, Bills): ").title().strip()
    if not category:
        print("Category cannot be empty.")
        return

    description = input("Description: ").strip()
    date_str = input("Date (YYYY-MM-DD, leave empty for today): ").strip() or today_iso()

    new_txn = {
        "id": _next_id_for_user(user["username"]),
        "username": user["username"],
        "type": t_type,
        "amount": float(amount),  # stored as float for simplicity
        "category": category,
        "date": date_str,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    _transactions.append(new_txn)
    save_transactions()
    print("Transaction added successfully!")

def view_transactions():
    if not um.is_logged_in():
        print("Please log in first.")
        return

    user = um.get_current_user()
    records = _user_transactions(user["username"])
    print(f"\n--- {user['username']}'s Transactions ---")

    if not records:
        print("No transactions found.")
        return

    print(f"{'ID':<5}{'TYPE':<10}{'AMOUNT':<10}{'CATEGORY':<15}{'DATE':<12}{'DESC'}")
    print("-" * 65)
    for t in records:
        print(f"{t['id']:<5}{t['type']:<10}{t['amount']:<10}{t['category']:<15}{t['date']:<12}{t.get('description','')}")
    print("-" * 65)

def edit_transaction():
    if not um.is_logged_in():
        print("Please log in first.")
        return

    view_transactions()
    try:
        txn_id = int(input("Enter the transaction ID to edit: ").strip())
    except Exception:
        print("Invalid ID.")
        return

    user = um.get_current_user()
    for t in _transactions:
        if t.get("id") == txn_id and t.get("username") == user["username"]:
            print("Leave a field blank to keep it unchanged.")

            new_type = input(f"New type ({t['type']}): ").strip().lower()
            if new_type:
                if new_type in ("income", "expense"):
                    t["type"] = new_type
                else:
                    print("Invalid type. Keeping old value.")

            new_amount = input(f"New amount ({t['amount']}): ").strip()
            if new_amount:
                try:
                    t["amount"] = float(Decimal(new_amount))
                except Exception:
                    print("Invalid amount. Keeping old value.")

            new_category = input(f"New category ({t['category']}): ").strip()
            if new_category:
                t["category"] = new_category

            new_desc = input(f"New description ({t['description']}): ").strip()
            if new_desc:
                t["description"] = new_desc

            new_date = input(f"New date ({t['date']}) [YYYY-MM-DD]: ").strip()
            if new_date:
                t["date"] = new_date

            t["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_transactions()
            print("Transaction updated successfully!")
            return

    print("Transaction not found.")

def delete_transaction():
    if not um.is_logged_in():
        print("Please log in first.")
        return

    view_transactions()
    try:
        txn_id = int(input("Enter the transaction ID to delete: ").strip())
    except Exception:
        print("Invalid ID.")
        return

    user = um.get_current_user()
    for t in list(_transactions):
        if t.get("id") == txn_id and t.get("username") == user["username"]:
            confirm = input("Are you sure you want to delete this? (y/n): ").lower()
            if confirm == "y":
                _transactions.remove(t)
                save_transactions()
                print("Transaction deleted.")
            else:
                print("Deletion cancelled.")
            return

    print("Transaction not found.")

# ---------- Menu ----------
def transaction_menu():
    while True:
        print("\n========== Transaction Menu ==========")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Edit Transaction")
        print("4. Delete Transaction")
        print("5. Back to Main Menu")
        print("======================================")

        choice = input("Enter your choice (1-5): ").strip()
        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            edit_transaction()
        elif choice == "4":
            delete_transaction()
        elif choice == "5":
            print("Returning to Main Menu...")
            break
        else:
            print("Invalid choice. Please enter a number from 1–5.")

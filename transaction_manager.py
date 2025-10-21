# transaction_manager.py
# Transactions backed by data_manager and session from user_manager.

from datetime import datetime, date
from decimal import Decimal
from typing import List

from data_manager import load_json, save_json, FILES
from utils import today_iso, get_number,ask_int_in_range ,get_choice
import user_manager as um
import ui

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
        ui.status_warn("Please log in first.")
        return

    user = um.get_current_user()
    ui.section("Add Transaction")
    t_type = get_choice("Type (income/expense): ", ["income", "expense"])

    amount = get_number("Amount: ")
    category = input("Category (e.g. Food, Salary, Bills): ").title().strip()
    if not category:
        ui.status_err("Category cannot be empty.")
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
    ui.status_ok("Transaction added successfully!")

def view_transactions():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return

    user = um.get_current_user()
    records = _user_transactions(user["username"])
    ui.section(f"{user['username']}'s Transactions")
    if not records:
        ui.status_warn("No transactions found.")
        return

    ui.table(
        rows=[(t['id'], t['type'], f"{t['amount']:.2f}", t['category'], t['date'], t.get('description', '')) for t in records],
        headers=("ID","TYPE","AMOUNT","CATEGORY","DATE","DESC"),
        align=["r","l","r","l","l","l"],
        pad=1
    )

def edit_transaction():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return

    view_transactions()
    txn_id = int(get_number("Enter the transaction ID to edit: "))

    user = um.get_current_user()
    for t in _transactions:
        if t.get("id") == txn_id and t.get("username") == user["username"]:
            print("Leave a field blank to keep it unchanged.")

            new_type = input(f"New type ({t['type']}): ").strip().lower()
            if new_type:
                if new_type in ("income", "expense"):
                    t["type"] = new_type
                else:
                    ui.status_warn("Invalid type. Keeping old value.")

            new_amount = input(f"New amount ({t['amount']}): ").strip()
            if new_amount:
                try:
                    t["amount"] = float(Decimal(new_amount))
                except Exception:
                    ui.status_warn("Invalid amount. Keeping old value.")

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
            ui.status_ok("Transaction updated successfully!")
            return

    ui.status_err("Transaction not found.")

def delete_transaction():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return

    view_transactions()
    txn_id = int(get_number("Enter the transaction ID to edit: "))

    user = um.get_current_user()
    for t in list(_transactions):
        if t.get("id") == txn_id and t.get("username") == user["username"]:
            confirm = input("Are you sure you want to delete this? (y/n): ").lower()
            if confirm == "y":
                _transactions.remove(t)
                save_transactions()
                ui.status_ok("Transaction deleted.")
            else:
                ui.status_warn("Deletion cancelled.")
            return

    ui.status_err("Transaction not found.")

# ---------- Menu ----------
def transaction_menu():
    while True:
        ui.section("Transaction Menu")
        print(f"{ui.FG['blue']}1.{ui.RESET} Add Transaction")
        print(f"{ui.FG['blue']}2.{ui.RESET} View Transactions")
        print(f"{ui.FG['blue']}3.{ui.RESET} Edit Transaction")
        print(f"{ui.FG['blue']}4.{ui.RESET} Delete Transaction")
        print(f"{ui.FG['blue']}5.{ui.RESET} Back to Main Menu")
        ui.line()

        choice = ask_int_in_range("Enter your choice (1–5): ", 1, 5)

        if choice == 1:
            add_transaction()
        elif choice == 2:
            view_transactions()
        elif choice == 3:
            edit_transaction()
        elif choice == 4:
            delete_transaction()
        elif choice == 5:
            ui.status_ok("Returning to Main Menu...")
            break

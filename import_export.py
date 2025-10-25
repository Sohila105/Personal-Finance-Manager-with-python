# import_export.py

import csv
from typing import List
from data_manager import FILES, save_json_with_backup, load_json
import user_manager as um
import transaction_manager as tm
import ui

def export_users_csv(path="data/users.csv"):
    users = um.get_users_data()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["username","currency","created_at"])
        w.writeheader()
        for u in users:
            w.writerow({"username":u.get("username",""),"currency":u.get("currency",""),"created_at":u.get("created_at","")})
    ui.status_ok(f"Users exported -> {path}")

def export_transactions_csv(path="data/transactions_all.csv", username: str | None = None):
    txns = tm.get_transactions_data()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","username","type","amount","category","date","description","created_at","updated_at"])
        w.writeheader()
        for t in txns:
            if username and t.get("username") != username:
                continue
            w.writerow(t)
    ui.status_ok(f"Transactions exported -> {path}")

def import_transactions_csv(path):
    """Append transactions from CSV into current dataset (expects same headers)."""
    rows = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    # normalize and append
    data = tm.get_transactions_data()
    count = 0
    for t in rows:
        try:
            t["id"] = int(t["id"])
            t["amount"] = float(t["amount"])
            data.append(t)
            count += 1
        except Exception:
            pass
    tm.save_transactions()
    ui.status_ok(f"Imported {count} transaction(s) from {path}")

def import_export_menu():
    while True:
        ui.section("CSV Import/Export")
        print(f"{ui.FG['blue']}1.{ui.RESET} Export Users CSV")
        print(f"{ui.FG['blue']}2.{ui.RESET} Export All Transactions CSV")
        print(f"{ui.FG['blue']}3.{ui.RESET} Export Current User Transactions CSV")
        print(f"{ui.FG['blue']}4.{ui.RESET} Import Transactions from CSV")
        print(f"{ui.FG['blue']}5.{ui.RESET} Back")
        ui.line()
        ch = input("Choose (1-5): ").strip()
        if ch == "1":
            export_users_csv()
        elif ch == "2":
            export_transactions_csv()
        elif ch == "3":
            if um.is_logged_in():
                export_transactions_csv(f"data/transactions_{um.get_current_user()['username']}.csv", um.get_current_user()["username"])
            else:
                ui.status_warn("Please log in first.")
        elif ch == "4":
            path = input("CSV path: ").strip()
            import_transactions_csv(path)
        elif ch == "5":
            break
        else:
            ui.status_warn("Invalid choice.")

# recurring_manager.py

from typing import List
from datetime import date, datetime
from decimal import Decimal
from data_manager import load_json, save_json_with_backup, FILES
from utils import get_nonempty_input, get_number, today_iso
import user_manager as um
import transaction_manager as tm
import ui

REC_PATH = FILES["recurring"]
_recurring: List[dict] = load_json(REC_PATH)

FREQS = ("daily","weekly","monthly")

def save_recurring():
    save_json_with_backup(REC_PATH, _recurring)

def add_rule():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    ui.section("Add Recurring Rule")
    rtype = input("Type (income/expense): ").lower().strip()
    if rtype not in ("income","expense"):
        ui.status_err("Invalid type.")
        return
    amount = get_number("Amount: ")
    category = get_nonempty_input("Category: ").title()
    freq = input("Frequency (daily/weekly/monthly): ").lower().strip()
    if freq not in FREQS:
        ui.status_err("Invalid frequency.")
        return
    next_date = input("Next date (YYYY-MM-DD, blank=today): ").strip() or today_iso()
    description = input("Description (optional): ").strip()

    rule = {
        "username": cu["username"],
        "type": rtype,
        "amount": float(amount),
        "category": category,
        "frequency": freq,
        "next_date": next_date,
        "description": description,
        "created_at": today_iso()
    }
    _recurring.append(rule)
    save_recurring()
    ui.status_ok("Recurring rule added.")

def view_rules():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    rules = [r for r in _recurring if r["username"]==cu["username"]]
    ui.section("Recurring Rules")
    if not rules:
        ui.status_warn("No rules.")
        return
    rows = [(r["type"], f"{r['amount']:.2f}", r["category"], r["frequency"], r["next_date"], r.get("description","")) for r in rules]
    ui.table(rows, headers=("TYPE","AMOUNT","CATEGORY","FREQ","NEXT DATE","DESC"))

def delete_rule():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    rules = [r for r in _recurring if r["username"]==cu["username"]]
    if not rules:
        ui.status_warn("No rules to delete.")
        return
    ui.section("Delete Rule")
    for i, r in enumerate(rules, start=1):
        print(f"{i}. {r['type']} {r['category']} {r['amount']} ({r['frequency']}) next {r['next_date']}")
    try:
        idx = int(input("Select rule #: ").strip())
        r = rules[idx-1]
    except Exception:
        ui.status_err("Invalid selection.")
        return
    confirm = input("Delete this rule? (y/n): ").lower()
    if confirm == "y":
        _recurring.remove(r)
        save_recurring()
        ui.status_ok("Rule deleted.")
    else:
        ui.status_warn("Deletion cancelled.")

def _advance(date_str: str, freq: str) -> str:
    y, m, d = map(int, date_str.split("-"))
    dt = date(y, m, d)
    if freq == "daily":
        nd = date.fromordinal(dt.toordinal()+1)
    elif freq == "weekly":
        nd = date.fromordinal(dt.toordinal()+7)
    else:  # monthly
        nm = m + 1
        ny = y + (nm-1)//12
        nm = 1 + (nm-1)%12
        # clamp day
        last_day = 28
        while True:
            try:
                nd = date(ny, nm, min(d, 31))
                break
            except ValueError:
                d -= 1
    return nd.isoformat()

def apply_due(today: str | None = None):
    """Generate transactions for rules due on/before today and advance 'next_date'."""
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    user_rules = [r for r in _recurring if r["username"]==cu["username"]]
    if not user_rules:
        ui.status_warn("No rules.")
        return
    today = today or date.today().isoformat()
    count = 0
    for r in user_rules:
        while r["next_date"] <= today:
            # create transaction
            tm.get_transactions_data().append({
                "id": _next_id_for_user(cu["username"]),
                "username": cu["username"],
                "type": r["type"],
                "amount": float(r["amount"]),
                "category": r["category"],
                "date": r["next_date"],
                "description": r.get("description","(recurring)"),
                "created_at": r["next_date"] + " 00:00:00",
                "updated_at": r["next_date"] + " 00:00:00",
            })
            r["next_date"] = _advance(r["next_date"], r["frequency"])
            count += 1
    tm.save_transactions()
    save_recurring()
    ui.status_ok(f"Applied {count} occurrence(s).")

def _next_id_for_user(username: str) -> int:
    from transaction_manager import get_transactions_data
    tx = [t["id"] for t in get_transactions_data() if t.get("username")==username]
    return (max(tx)+1) if tx else 1

def recurring_menu():
    while True:
        ui.section("Recurring")
        print(f"{ui.FG['blue']}1.{ui.RESET} Add Rule")
        print(f"{ui.FG['blue']}2.{ui.RESET} View Rules")
        print(f"{ui.FG['blue']}3.{ui.RESET} Apply Due Now")
        print(f"{ui.FG['blue']}4.{ui.RESET} Delete Rule")
        print(f"{ui.FG['blue']}5.{ui.RESET} Back")
        ui.line()
        ch = input("Choose (1-5): ").strip()
        if ch == "1": add_rule()
        elif ch == "2": view_rules()
        elif ch == "3": apply_due()
        elif ch == "4": delete_rule()
        elif ch == "5": break
        else: ui.status_warn("Invalid choice.")

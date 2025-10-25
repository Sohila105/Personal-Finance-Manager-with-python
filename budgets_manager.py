# budgets_manager.py

from typing import List
from collections import defaultdict
from datetime import date
from decimal import Decimal
from data_manager import load_json, save_json_with_backup, FILES
from utils import get_nonempty_input, get_number, fmt_money
import user_manager as um
import ui
import transaction_manager as tm

BUDGETS_PATH = FILES["budgets"]
_budgets: List[dict] = load_json(BUDGETS_PATH)

def save_budgets():
    save_json_with_backup(BUDGETS_PATH, _budgets)

def _ym(dt: str) -> str:
    # dt is "YYYY-MM-DD"
    return dt[:7] if len(dt) >= 7 else ""

def set_budget():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    ui.section("Set Monthly Budget")
    category = get_nonempty_input("Category: ").title()
    month = input("Month (YYYY-MM, blank = current): ").strip() or date.today().strftime("%Y-%m")
    limit_amt = get_number("Monthly limit: ")

    # upsert
    existing = next((b for b in _budgets if b["username"]==cu["username"] and b["category"]==category and b["month"]==month), None)
    if existing:
        existing["limit"] = float(limit_amt)
    else:
        _budgets.append({"username": cu["username"], "category": category, "limit": float(limit_amt), "month": month})
    save_budgets()
    ui.status_ok("Budget saved.")

def view_budgets():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    month = input("Month (YYYY-MM, blank = current): ").strip() or date.today().strftime("%Y-%m")

    # sum expenses by category for this month
    txns = [t for t in tm.get_transactions_data() if t.get("username")==cu["username"] and _ym(t.get("date",""))==month and t.get("type")=="expense"]
    spent = defaultdict(Decimal)
    for t in txns:
        spent[t["category"]] += Decimal(str(t["amount"]))

    rows = []
    any_budget = False
    for b in [x for x in _budgets if x["username"]==cu["username"] and x["month"]==month]:
        any_budget = True
        cat = b["category"]
        limit = Decimal(str(b["limit"]))
        used  = spent.get(cat, Decimal("0"))
        pct = (used/limit*100) if limit>0 else Decimal("0")
        status = "OK"
        color = ui.FG["green"]
        if used >= limit:
            status = "OVER"
            color = ui.FG["red"]
        bar = _bar(int(pct))
        rows.append((cat, f"{bar} {pct:.0f}%", fmt_money(used, cu["currency"]), fmt_money(limit, cu["currency"]), color+status+ui.RESET))
    ui.section(f"Budgets — {month}")
    if not any_budget:
        ui.status_warn("No budgets set for this month.")
    else:
        ui.table(rows, headers=("CATEGORY","PROGRESS","SPENT","LIMIT","STATUS"), align=["l","l","r","r","c"])

def _bar(pct: int, width=20):
    filled = max(0, min(width, int(width * pct / 100)))
    return ui.FG["yellow"] + "█"*filled + ui.RESET + "·"*(width-filled)

def budgets_menu():
    while True:
        ui.section("Budgets")
        print(f"{ui.FG['blue']}1.{ui.RESET} Set/Update Budget")
        print(f"{ui.FG['blue']}2.{ui.RESET} View Budgets")
        print(f"{ui.FG['blue']}3.{ui.RESET} Back")
        ui.line()
        choice = input("Choose (1-3): ").strip()
        if choice == "1": set_budget()
        elif choice == "2": view_budgets()
        elif choice == "3": break
        else: ui.status_warn("Invalid choice.")

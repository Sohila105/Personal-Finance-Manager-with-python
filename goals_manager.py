# goals_manager.py

from typing import List
from decimal import Decimal
from data_manager import load_json, save_json_with_backup, FILES
from utils import get_nonempty_input, get_number, today_iso, to_decimal, fmt_money
import user_manager as um
import ui

GOALS_PATH = FILES["goals"]
_goals: List[dict] = load_json(GOALS_PATH)

def _user_goals(username: str) -> List[dict]:
    return [g for g in _goals if g.get("username") == username]

def save_goals():
    save_json_with_backup(GOALS_PATH, _goals)

def add_goal():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    ui.section("Add Savings Goal")
    name = get_nonempty_input("Goal name: ")
    target = get_number("Target amount: ")
    deadline = input("Deadline (YYYY-MM-DD, optional): ").strip()

    g = {
        "username": cu["username"],
        "goal_name": name,
        "target_amount": float(target),
        "saved_so_far": 0.0,
        "deadline": deadline or "",
        "created_at": today_iso(),
    }
    _goals.append(g)
    save_goals()
    ui.status_ok("Goal added.")

def update_progress():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    goals = _user_goals(cu["username"])
    if not goals:
        ui.status_warn("No goals yet.")
        return

    ui.section("Update Goal Progress")
    for i, g in enumerate(goals, start=1):
        print(f"{i}. {g['goal_name']} — target {fmt_money(g['target_amount'], cu['currency'])}, saved {fmt_money(g['saved_so_far'], cu['currency'])}")
    try:
        idx = int(input("Select goal #: ").strip())
        g = goals[idx-1]
    except Exception:
        ui.status_err("Invalid selection.")
        return

    amt = get_number("Add amount to saved: ", allow_zero=False)
    g["saved_so_far"] = float(to_decimal(g["saved_so_far"]) + amt)
    save_goals()
    ui.status_ok("Progress updated.")

def view_goals():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    goals = _user_goals(cu["username"])
    ui.section("Savings Goals")
    if not goals:
        ui.status_warn("No goals yet.")
        return

    rows = []
    for g in goals:
        target = to_decimal(g["target_amount"])
        saved  = to_decimal(g["saved_so_far"])
        pct = (saved / target * 100) if target > 0 else Decimal("0")
        bar = _bar(int(pct))
        rows.append((g["goal_name"], f"{bar} {pct:.0f}%", fmt_money(saved, cu["currency"]), fmt_money(target, cu["currency"]), g.get("deadline","")))
    ui.table(rows, headers=("GOAL","PROGRESS","SAVED","TARGET","DEADLINE"), align=["l","l","r","r","l"])

def delete_goal():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    goals = _user_goals(cu["username"])
    if not goals:
        ui.status_warn("No goals to delete.")
        return
    ui.section("Delete Goal")
    for i, g in enumerate(goals, start=1):
        print(f"{i}. {g['goal_name']}")
    try:
        idx = int(input("Select goal #: ").strip())
        g = goals[idx-1]
    except Exception:
        ui.status_err("Invalid selection.")
        return

    confirm = input(f"Delete '{g['goal_name']}'? (y/n): ").lower()
    if confirm == "y":
        _goals.remove(g)
        save_goals()
        ui.status_ok("Goal deleted.")
    else:
        ui.status_warn("Deletion cancelled.")

def _bar(pct: int, width=20):
    filled = max(0, min(width, int(width * pct / 100)))
    return ui.FG["green"] + "█"*filled + ui.RESET + "·"*(width-filled)

def goals_menu():
    while True:
        ui.section("Goals")
        print(f"{ui.FG['blue']}1.{ui.RESET} Add Goal")
        print(f"{ui.FG['blue']}2.{ui.RESET} View Goals")
        print(f"{ui.FG['blue']}3.{ui.RESET} Update Progress")
        print(f"{ui.FG['blue']}4.{ui.RESET} Delete Goal")
        print(f"{ui.FG['blue']}5.{ui.RESET} Back")
        ui.line()
        choice = input("Choose (1-5): ").strip()
        if choice == "1": add_goal()
        elif choice == "2": view_goals()
        elif choice == "3": update_progress()
        elif choice == "4": delete_goal()
        elif choice == "5": break
        else: ui.status_warn("Invalid choice.")

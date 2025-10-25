# reminders_manager.py

from typing import List
from datetime import date, datetime, timedelta
from data_manager import load_json, save_json_with_backup, FILES
from utils import get_nonempty_input, today_iso
import user_manager as um
import ui

REM_PATH = FILES["reminders"]
_reminders: List[dict] = load_json(REM_PATH)

def save_reminders():
    save_json_with_backup(REM_PATH, _reminders)

def add_reminder():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    ui.section("Add Reminder")
    title = get_nonempty_input("Title: ")
    due_date = get_nonempty_input("Due date (YYYY-MM-DD): ")
    notes = input("Notes (optional): ").strip()
    r = {"username": cu["username"], "title": title, "due_date": due_date, "notes": notes, "created_at": today_iso()}
    _reminders.append(r)
    save_reminders()
    ui.status_ok("Reminder added.")

def view_reminders():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    rs = [r for r in _reminders if r["username"]==cu["username"]]
    ui.section("Reminders")
    if not rs:
        ui.status_warn("No reminders.")
        return
    rows = [(r["due_date"], r["title"], r.get("notes","")) for r in sorted(rs, key=lambda x: x["due_date"])]
    ui.table(rows, headers=("DUE DATE","TITLE","NOTES"))

def due_soon(days=7):
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    today = date.today()
    lim = today + timedelta(days=days)
    rs = [r for r in _reminders if r["username"]==cu["username"] and today.isoformat() <= r["due_date"] <= lim.isoformat()]
    ui.section(f"Due within {days} day(s)")
    if not rs:
        ui.status_warn("Nothing due soon.")
        return
    rows = [(r["due_date"], r["title"], r.get("notes","")) for r in sorted(rs, key=lambda x: x["due_date"])]
    ui.table(rows, headers=("DUE DATE","TITLE","NOTES"))

def delete_reminder():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    rs = [r for r in _reminders if r["username"]==cu["username"]]
    if not rs:
        ui.status_warn("No reminders to delete.")
        return
    ui.section("Delete Reminder")
    for i, r in enumerate(rs, start=1):
        print(f"{i}. {r['due_date']} — {r['title']}")
    try:
        idx = int(input("Select #: ").strip())
        r = rs[idx-1]
    except Exception:
        ui.status_err("Invalid selection.")
        return
    if input("Delete? (y/n): ").lower() == "y":
        _reminders.remove(r)
        save_reminders()
        ui.status_ok("Reminder deleted.")
    else:
        ui.status_warn("Deletion cancelled.")

def reminders_menu():
    while True:
        ui.section("Reminders")
        print(f"{ui.FG['blue']}1.{ui.RESET} Add Reminder")
        print(f"{ui.FG['blue']}2.{ui.RESET} View All")
        print(f"{ui.FG['blue']}3.{ui.RESET} Due Soon (7 days)")
        print(f"{ui.FG['blue']}4.{ui.RESET} Delete Reminder")
        print(f"{ui.FG['blue']}5.{ui.RESET} Back")
        ui.line()
        ch = input("Choose (1-5): ").strip()
        if ch == "1": add_reminder()
        elif ch == "2": view_reminders()
        elif ch == "3": due_soon()
        elif ch == "4": delete_reminder()
        elif ch == "5": break
        else: ui.status_warn("Invalid choice.")

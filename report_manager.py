# report_manager.py
# Read-only analytics over transactions.

from datetime import date
from decimal import Decimal
from collections import defaultdict
from typing import List, Dict, Any, Tuple

from data_manager import load_json, FILES
from utils import fmt_money, parse_date, to_decimal
import user_manager as um
import ui

TXNS_PATH = FILES["transactions"]

def _load_user_transactions() -> List[Dict[str, Any]]:
    if not um.is_logged_in():
        return []
    cu = um.get_current_user()
    all_txns = load_json(TXNS_PATH)
    return [t for t in all_txns if t.get("username") == cu["username"]]

def _safe_in_month(date_str: str, y: int, m: int) -> bool:
    try:
        d = parse_date(date_str)
        return d.year == y and d.month == m
    except Exception:
        return False

def _totals(txns: List[Dict[str, Any]]) -> Tuple[Decimal, Decimal, Decimal]:
    inc = Decimal("0")
    exp = Decimal("0")
    for t in txns:
        amt = to_decimal(t.get("amount", 0))
        if t.get("type") == "income":
            inc += amt
        elif t.get("type") == "expense":
            exp += amt
    return inc, exp, inc - exp

def _group_by_month(txns: List[Dict[str, Any]]) -> Dict[Tuple[int, int], List[Dict[str, Any]]]:
    buckets: Dict[Tuple[int, int], List[Dict[str, Any]]] = defaultdict(list)
    for t in txns:
        try:
            d = parse_date(t["date"])
        except Exception:
            continue
        buckets[(d.year, d.month)].append(t)
    return dict(buckets)

def _group_by_category(txns: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    totals: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for t in txns:
        if t.get("type") == "expense":
            cat = (t.get("category") or "Uncategorized").strip()
            totals[cat] += to_decimal(t.get("amount", 0))
    return dict(totals)

def _month_name(y, m):
    return date(y, m, 1).strftime("%b %Y")

def _bar_from_pct(pct: Decimal, width: int = 20) -> str:
    filled = int((float(pct) / 100) * width + 0.5)
    filled = max(0, min(filled, width))
    return "█" * filled + "·" * (width - filled)

# -----------------------------
# Reports
# -----------------------------
def dashboard_summary():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return

    cu = um.get_current_user()
    txns = _load_user_transactions()
    ui.section("Dashboard")
    if not txns:
        ui.status_warn("No transactions yet.")
        return

    total_inc, total_exp, net_all = _totals(txns)

    today = date.today()
    ym_txns = [t for t in txns if _safe_in_month(t.get("date"), today.year, today.month)]
    m_inc, m_exp, m_net = _totals(ym_txns)

    print(f"{ui.BOLD}User:{ui.RESET} {cu['username']}    {ui.BOLD}Currency:{ui.RESET} {cu['currency']}")
    ui.line()
    print(f"{ui.FG['green']}Total Income{ui.RESET} : {fmt_money(total_inc, cu['currency'])}")
    print(f"{ui.FG['red']}Total Expense{ui.RESET}: {fmt_money(total_exp, cu['currency'])}")
    print(f"{ui.FG['cyan']}Net (All){ui.RESET}    : {fmt_money(net_all, cu['currency'])}")
    ui.line()
    print(f"This Month ({today.strftime('%b %Y')})")
    print(f"  Income : {fmt_money(m_inc, cu['currency'])}")
    print(f"  Expense: {fmt_money(m_exp, cu['currency'])}")
    print(f"  Net    : {fmt_money(m_net, cu['currency'])}")
    ui.line()
    print("Recent Transactions (latest 5):")
    for t in sorted(txns, key=lambda x: x.get("date", ""), reverse=True)[:5]:
        print(f"  {t['date']}  {t['type']:<7}  {t['category']:<14}  {fmt_money(to_decimal(t['amount']), cu['currency'])}  - {t.get('description','')}")

def monthly_report():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return

    cu = um.get_current_user()
    try:
        year = int(input("Year (e.g., 2025): ").strip())
        month = int(input("Month (1-12): ").strip())
        _ = date(year, month, 1)
    except Exception:
        ui.status_err("Invalid year/month.")
        return

    txns = _load_user_transactions()
    m_txns = [t for t in txns if _safe_in_month(t.get("date"), year, month)]
    inc, exp, net = _totals(m_txns)

    ui.section(f"Monthly Report: {_month_name(year, month)}")
    print(f"Income : {fmt_money(inc, cu['currency'])}")
    print(f"Expense: {fmt_money(exp, cu['currency'])}")
    print(f"Net    : {fmt_money(net, cu['currency'])}")

    if not m_txns:
        ui.status_warn("No transactions for this month.")
        return

    ui.line()
    headers = ("DATE","TYPE","AMOUNT","CATEGORY","DESC")
    rows = [(t['date'], t['type'], fmt_money(to_decimal(t['amount']), cu['currency']), t['category'], t.get('description','')) for t in sorted(m_txns, key=lambda x: x.get("date"))]
    ui.table(rows, headers=headers, align=["l","l","r","l","l"])

def category_breakdown():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return

    cu = um.get_current_user()
    txns = _load_user_transactions()

    scope = input("Filter by a specific month? (y/n): ").lower().strip()
    title = "Category Breakdown – All Time"
    if scope == "y":
        try:
            year = int(input("Year (e.g., 2025): ").strip())
            month = int(input("Month (1-12): ").strip())
            _ = date(year, month, 1)
            txns = [t for t in txns if _safe_in_month(t.get("date"), year, month)]
            title = f"Category Breakdown – {_month_name(year, month)}"
        except Exception:
            ui.status_err("Invalid year/month.")
            return

    cat_totals = _group_by_category(txns)
    total_exp = sum(cat_totals.values(), Decimal("0"))

    ui.section(title)
    if total_exp == 0:
        ui.status_warn("No expense data to show.")
        return

    rows = []
    for cat, amt in sorted(cat_totals.items(), key=lambda kv: kv[1], reverse=True):
        pct = (amt / total_exp * 100) if total_exp > 0 else Decimal("0")
        bar = _bar_from_pct(pct)
        rows.append((cat, fmt_money(amt, cu['currency']), f"{bar} {pct:.1f}%"))
    ui.table(rows, headers=("CATEGORY","AMOUNT","SHARE"), align=["l","r","l"])

def spending_trend():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return

    cu = um.get_current_user()
    txns = _load_user_transactions()
    buckets = _group_by_month(txns)

    try:
        n = int(input("How many recent months to show? (e.g., 6): ").strip() or "6")
    except Exception:
        n = 6

    if not buckets:
        ui.status_warn("No transactions to chart.")
        return

    ordered = sorted(buckets.keys())[-n:]
    ui.section("Spending Trend (Net per Month)")
    max_abs = Decimal("0")
    nets = []
    for y, m in ordered:
        inc, exp, net = _totals(buckets[(y, m)])
        nets.append((_month_name(y, m), net))
        if abs(net) > max_abs:
            max_abs = abs(net)
    if max_abs == 0:
        max_abs = Decimal("1")

    width = 24
    for label, net in nets:
        ratio = (abs(net) / max_abs)                      # Decimal
        units = int(ratio * Decimal(width) + Decimal("0.5"))  # keep all Decimal
        if net >= 0:
            line = " " * width + "|" + ui.FG["green"] + "█" * units + ui.RESET
        else:
            line = " " * (width - units) + ui.FG["red"] + "█" * units + ui.RESET + "|"
        print(f"{label:<12} {line}  {fmt_money(net, cu['currency'])}")

def search_filter():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return

    cu = um.get_current_user()
    txns = _load_user_transactions()
    if not txns:
        ui.status_warn("No transactions found.")
        return

    ui.section("Search & Filter")
    start = input("Start date (YYYY-MM-DD, blank for none): ").strip()
    end = input("End date (YYYY-MM-DD, blank for none): ").strip()
    cat = input("Category contains (blank = any): ").strip().lower()
    min_amt = input("Min amount (blank = any): ").strip()
    max_amt = input("Max amount (blank = any): ").strip()
    sort_by = input("Sort by (date/amount/category/type) [date]: ").strip().lower() or "date"
    order = input("Order (asc/desc) [asc]: ").strip().lower() or "asc"

    filtered = []
    for t in txns:
        try:
            d = parse_date(t["date"])
        except Exception:
            continue
        if start:
            try:
                if d < parse_date(start):
                    continue
            except Exception:
                ui.status_warn("Invalid start date; ignoring.")
        if end:
            try:
                if d > parse_date(end):
                    continue
            except Exception:
                ui.status_warn("Invalid end date; ignoring.")

        if cat and cat not in (t.get("category", "").lower()):
            continue

        amt = to_decimal(t.get("amount", 0))
        if min_amt:
            try:
                if amt < to_decimal(min_amt):
                    continue
            except Exception:
                ui.status_warn("Invalid min amount; ignoring.")
        if max_amt:
            try:
                if amt > to_decimal(max_amt):
                    continue
            except Exception:
                ui.status_warn("Invalid max amount; ignoring.")

        filtered.append(t)

    key_funcs = {
        "date": lambda x: x.get("date", ""),
        "amount": lambda x: to_decimal(x.get("amount", 0)),
        "category": lambda x: x.get("category", ""),
        "type": lambda x: x.get("type", ""),
    }
    key_fn = key_funcs.get(sort_by, key_funcs["date"])
    reverse = (order == "desc")
    filtered.sort(key=key_fn, reverse=reverse)

    if not filtered:
        ui.status_warn("No matching transactions.")
        return

    ui.line()
    headers = ("DATE","TYPE","AMOUNT","CATEGORY","DESC")
    rows = [(t['date'], t['type'], fmt_money(to_decimal(t['amount']), cu['currency']), t['category'], t.get('description','')) for t in filtered]
    ui.table(rows, headers=headers, align=["l","l","r","l","l"])

def reports_menu():
    while True:
        ui.section("Reports")
        print(f"{ui.FG['blue']}1.{ui.RESET} Dashboard Summary")
        print(f"{ui.FG['blue']}2.{ui.RESET} Monthly Report")
        print(f"{ui.FG['blue']}3.{ui.RESET} Category Breakdown")
        print(f"{ui.FG['blue']}4.{ui.RESET} Spending Trend (ASCII)")
        print(f"{ui.FG['blue']}5.{ui.RESET} Search & Filter")
        print(f"{ui.FG['blue']}6.{ui.RESET} Back to Main Menu")
        ui.line()

        choice = input("Enter your choice (1-6): ").strip()
        if choice == "1":
            dashboard_summary()
        elif choice == "2":
            monthly_report()
        elif choice == "3":
            category_breakdown()
        elif choice == "4":
            spending_trend()
        elif choice == "5":
            search_filter()
        elif choice == "6":
            ui.status_ok("Returning to Main Menu...")
            break
        else:
            ui.status_warn("Invalid choice. Please enter a number 1–6.")

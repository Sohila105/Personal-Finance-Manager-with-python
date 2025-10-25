# health_manager.py

from decimal import Decimal
from collections import defaultdict
from datetime import date
from typing import List, Dict
import user_manager as um
from data_manager import load_json, FILES
from utils import to_decimal, fmt_money
import ui

TXNS_PATH = FILES["transactions"]

def _load_user_txns():
    from data_manager import load_json
    if not um.is_logged_in():
        return []
    cu = um.get_current_user()
    return [t for t in load_json(TXNS_PATH) if t.get("username")==cu["username"]]

def health_score():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    txns = _load_user_txns()
    if not txns:
        ui.status_warn("No data for scoring.")
        return

    # last 3 months income/expense
    buckets = defaultdict(lambda: {"inc":Decimal("0"),"exp":Decimal("0")})
    for t in txns:
        y,m = t["date"][:4], t["date"][5:7]
        key = f"{y}-{m}"
        amt = to_decimal(t["amount"])
        if t["type"]=="income":
            buckets[key]["inc"] += amt
        elif t["type"]=="expense":
            buckets[key]["exp"] += amt
    months = sorted(buckets.keys())[-3:]
    if not months:
        ui.status_warn("Not enough data.")
        return

    inc = sum((buckets[m]["inc"] for m in months), Decimal("0")) / max(1,len(months))
    exp = sum((buckets[m]["exp"] for m in months), Decimal("0")) / max(1,len(months))
    net = inc - exp
    savings_rate = (net/inc*100) if inc > 0 else Decimal("0")

    # volatility proxy: expense std / mean (rough)
    vals = [buckets[m]["exp"] for m in months]
    mean = sum(vals, Decimal("0")) / max(1,len(vals))
    var = sum((v-mean)**2 for v in vals) / max(1,len(vals))
    # normalize score: higher savings rate and lower volatility -> higher score
    rate_score = min(100, max(0, float(savings_rate)))          # 0..100
    vol_penalty = min(40, 40 * float((var**0.5) / (mean+Decimal("1"))))  # cap
    score = max(0, min(100, rate_score - vol_penalty))

    ui.section("Financial Health Score")
    print(f"Avg Monthly Income : {fmt_money(inc, cu['currency'])}")
    print(f"Avg Monthly Expense: {fmt_money(exp, cu['currency'])}")
    print(f"Avg Monthly Net    : {fmt_money(net, cu['currency'])}")
    print(f"Savings Rate       : {savings_rate:.1f}%")
    ui.line()
    bar = "█"*int(score/5) + "·"*int((100-score)/5)
    color = ui.FG["green"] if score>=70 else (ui.FG["yellow"] if score>=40 else ui.FG["red"])
    print(f"Score: {color}{score:.0f}{ui.RESET}/100  {bar}")

def health_menu():
    while True:
        ui.section("Financial Health")
        print(f"{ui.FG['blue']}1.{ui.RESET} Calculate Health Score")
        print(f"{ui.FG['blue']}2.{ui.RESET} Back")
        ui.line()
        ch = input("Choose (1-2): ").strip()
        if ch == "1": health_score()
        elif ch == "2": break
        else: ui.status_warn("Invalid choice.")

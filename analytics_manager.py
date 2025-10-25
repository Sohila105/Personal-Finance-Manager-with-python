# analytics_manager.py

from decimal import Decimal
from collections import defaultdict
from datetime import date
from typing import List, Dict
from data_manager import load_json, FILES
import user_manager as um
from utils import to_decimal, fmt_money
import ui

TXNS_PATH = FILES["transactions"]

def predict_next_month_net():
    if not um.is_logged_in():
        ui.status_warn("Please log in first.")
        return
    cu = um.get_current_user()
    txns = [t for t in load_json(TXNS_PATH) if t.get("username")==cu["username"]]
    if not txns:
        ui.status_warn("No data for prediction.")
        return

    # net per month
    buckets = defaultdict(lambda: Decimal("0"))
    for t in txns:
        ym = t["date"][:7]
        amt = to_decimal(t["amount"])
        buckets[ym] += amt if t["type"]=="income" else -amt
    months = sorted(buckets.keys())
    if len(months) < 2:
        ui.status_warn("Need at least 2 months of data.")
        return

    # simple linear trend on index vs net
    nets = [buckets[m] for m in months]
    n = len(nets)
    xs = list(range(n))
    x_mean = sum(xs)/n
    y_mean = sum(float(v) for v in nets)/n
    num = sum((x-x_mean)*(float(y)-y_mean) for x,y in zip(xs,nets))
    den = sum((x-x_mean)**2 for x in xs) or 1
    slope = num/den
    intercept = y_mean - slope*x_mean
    next_x = n
    pred = Decimal(str(intercept + slope*next_x))

    ui.section("Predictive Analytics")
    print(f"Trend based on {n} month(s).")
    print(f"Predicted Net for next month: {fmt_money(pred, cu['currency'])}")

def analytics_menu():
    while True:
        ui.section("Analytics")
        print(f"{ui.FG['blue']}1.{ui.RESET} Predict Next Month Net")
        print(f"{ui.FG['blue']}2.{ui.RESET} Back")
        ui.line()
        ch = input("Choose (1-2): ").strip()
        if ch == "1": predict_next_month_net()
        elif ch == "2": break
        else: ui.status_warn("Invalid choice.")

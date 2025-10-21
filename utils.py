# utils.py
# Shared validation, formatting, and menu helpers.

from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# --- Conversion & Formatting ---

def to_decimal(value):
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Invalid numeric value: {value!r}")

def fmt_money(value, currency=None):
    try:
        d = to_decimal(value)
    except Exception:
        return str(value)
    s = f"{d:.2f}"
    return f"{s} {currency}" if currency else s

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def today_iso():
    return date.today().isoformat()

# --- Input Validation Helpers ---

def get_nonempty_input(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("Input cannot be empty. Try again.")

def get_choice(prompt, choices):
    choices = [c.lower() for c in choices]
    while True:
        v = input(prompt).strip().lower()
        if v in choices:
            return v
        print(f"Invalid choice. Options: {', '.join(choices)}")

def get_number(prompt, allow_zero=False):
    while True:
        val = input(prompt).strip()
        try:
            n = to_decimal(val)
            if not allow_zero and n <= 0:
                print("Number must be greater than 0.")
                continue
            return n
        except ValueError:
            print("Invalid number. Try again.")

def ask_int_in_range(prompt, min_val, max_val):
    while True:
        v = input(prompt).strip()
        if not v.isdigit():
            print("Please enter a valid number.")
            continue
        num = int(v)
        if num < min_val or num > max_val:
            print(f"Value must be between {min_val} and {max_val}.")
        else:
            return num

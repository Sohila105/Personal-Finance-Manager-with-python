# ui.py
# Terminal UI helpers: colors, banners, boxes, tables, status lines.

import os
import shutil
from datetime import datetime

# --- color support (safe fallback) ---
RESET = ""
BOLD = ""
DIM = ""
FG = {"grey":"", "red":"", "green":"", "yellow":"", "blue":"", "magenta":"", "cyan":"", "white":""}

def _enable_colors():
    global RESET, BOLD, DIM, FG
    try:
        # Optional dependency; improves Windows support
        from colorama import init, Fore, Style
        init(autoreset=True)
        RESET = Style.RESET_ALL
        BOLD  = Style.BRIGHT
        DIM   = Style.DIM
        FG = {
            "grey": Fore.LIGHTBLACK_EX, "red": Fore.RED, "green": Fore.GREEN, "yellow": Fore.YELLOW,
            "blue": Fore.BLUE, "magenta": Fore.MAGENTA, "cyan": Fore.CYAN, "white": Fore.WHITE
        }
    except Exception:
        # ANSI fallback (works on Unix-like and modern Windows terminals)
        RESET = "\033[0m"
        BOLD  = "\033[1m"
        DIM   = "\033[2m"
        FG = {
            "grey":"\033[90m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m",
            "blue":"\033[34m", "magenta":"\033[35m", "cyan":"\033[36m", "white":"\033[97m"
        }

_enable_colors()

# --- layout helpers ---
def term_width(default=80) -> int:
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def line(char="─", pad=0):
    print((" " * pad) + (char * max(20, term_width()-pad)))

def banner(title: str, subtitle: str | None = None):
    w = term_width()
    print(FG["cyan"] + "═" * w + RESET)
    print((FG["cyan"] + BOLD + f"{title}".center(w) + RESET))
    if subtitle:
        print((FG["cyan"] + DIM + f"{subtitle}".center(w) + RESET))
    print(FG["cyan"] + "═" * w + RESET)

def section(title: str):
    print("\n" + FG["yellow"] + BOLD + f"— {title} —" + RESET)

def status_ok(msg: str):
    print(FG["green"] + "✔ " + msg + RESET)

def status_warn(msg: str):
    print(FG["yellow"] + "⚠ " + msg + RESET)

def status_err(msg: str):
    print(FG["red"] + "✖ " + msg + RESET)

def stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- table helper (monospace) ---
def table(rows, headers=None, align=None, pad=1):
    """
    rows: list of sequences
    headers: sequence or None
    align: per-column 'l'/'r'/'c' or single char applied to all
    """
    if not rows and not headers:
        return
    cols = len(headers) if headers else len(rows[0])
    widths = [0]*cols
    data = []
    if headers:
        widths = [max(w, len(str(h))) for w, h in zip(widths, headers)]
    for r in rows:
        sr = [str(c) for c in r]
        data.append(sr)
        widths = [max(w, len(c)) for w, c in zip(widths, sr)]

    def fmt_cell(c, w, a):
        if a == "r":
            return c.rjust(w)
        if a == "c":
            return c.center(w)
        return c.ljust(w)

    if isinstance(align, str):
        align = [align]*cols
    if not align:
        align = ["l"]*cols

    # Header
    if headers:
        print(" " * pad + FG["magenta"] + BOLD + " | ".join(fmt_cell(str(h), w, "c") for h, w in zip(headers, widths)) + RESET)
        print(" " * pad + FG["magenta"] + "-" * (sum(widths) + 3*(cols-1)) + RESET)

    # Rows
    for r in data:
        print(" " * pad + " | ".join(fmt_cell(c, w, a) for c, w, a in zip(r, widths, align)))

# --- menu helper ---
def menu(title, items):
    """
    items: list of (key_str, label)
    """
    section(title)
    for k, label in items:
        print(f"{FG['blue']}{k}.{RESET} {label}")

# main.py
# Orchestrates menus and one-shot save-all on exit (with backups).

import user_manager as um
import transaction_manager as tm
import report_manager as rm
from data_manager import save_all, FILES, load_json
import ui

# NEW imports
import goals_manager as gm
import budgets_manager as bm
import recurring_manager as rc
import reminders_manager as rem
import import_export as ie
import health_manager as hm
import analytics_manager as an

def main_menu():
    while True:
        ui.clear()
        ui.banner("Personal Finance Manager", f"{ui.stamp()}")
        cu = um.get_current_user()
        if cu:
            print(f"{ui.BOLD}{ui.FG['green']}Logged in as:{ui.RESET} {cu['username']} ({cu['currency']})")
        else:
            print(f"{ui.FG['grey']}Not logged in{ui.RESET}")

        ui.menu("User", [("1","Register"),("2","Login"),("3","Logout")])
        ui.menu("Transactions", [("4","Manage Transactions")])
        ui.menu("Reports", [("5","Reports")])
        ui.menu("Goals", [("6","Savings Goals")])
        ui.menu("Budgets", [("7","Monthly Budgets")])
        ui.menu("Recurring", [("8","Recurring Transactions")])
        ui.menu("Reminders", [("9","Bill Reminders")])
        ui.menu("Data", [("10","CSV Import/Export")])
        ui.menu("Health", [("11","Financial Health Score")])
        ui.menu("Analytics", [("12","Predictive Analytics")])
        print()
        print(f"{ui.FG['blue']}13.{ui.RESET} Save & Exit")
        ui.line()

        choice = input("Enter your choice (1-13): ").strip()

        if choice == "1": um.register_user()
        elif choice == "2": um.login_user()
        elif choice == "3": um.logout_user()
        elif choice == "4": tm.transaction_menu()
        elif choice == "5": rm.reports_menu()
        elif choice == "6": gm.goals_menu()
        elif choice == "7": bm.budgets_menu()
        elif choice == "8": rc.recurring_menu()
        elif choice == "9": rem.reminders_menu()
        elif choice == "10": ie.import_export_menu()
        elif choice == "11": hm.health_menu()
        elif choice == "12": an.analytics_menu()
        elif choice == "13":
            ui.status_ok("Saving data and exiting... Goodbye.")
            datasets = {
                "users": um.get_users_data(),
                "transactions": tm.get_transactions_data(),
                "goals": load_json(FILES["goals"]),
                "budgets": load_json(FILES["budgets"]),
                "reminders": load_json(FILES["reminders"]),
                "recurring": load_json(FILES["recurring"]),
            }
            save_all(datasets)
            break
        else:
            ui.status_warn("Invalid choice.")

def show_help():
    ui.section("Help - Main Menu")
    print("1. Register  - Create a new user account.")
    print("2. Login     - Log into an existing account.")
    print("3. Logout    - Log out the current user.")
    print("4. Manage Transactions  - Add, view, edit, or delete financial records.")
    print("5. Reports   - Generate spending or income reports.")
    print("6. Save & Exit - Save all data and exit safely.")
    ui.line()
    input("Press Enter to return to the main menu...")


if __name__ == "__main__":
    main_menu()

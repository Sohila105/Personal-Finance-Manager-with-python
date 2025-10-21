# main.py
# Orchestrates menus and one-shot save-all on exit (with backups).

import user_manager as um
import transaction_manager as tm
import report_manager as rm
from data_manager import save_all
import ui

def main_menu():
    while True:
        ui.clear()
        ui.banner("Personal Finance Manager", f"{ui.stamp()}")
        cu = um.get_current_user()
        if cu:
            print(f"{ui.BOLD}{ui.FG['green']}Logged in as:{ui.RESET} {cu['username']} ({cu['currency']})")
        else:
            print(f"{ui.FG['grey']}Not logged in{ui.RESET}")

        ui.menu("User", [("1", "Register"), ("2", "Login"), ("3", "Logout")])
        ui.menu("Transactions", [("4", "Manage Transactions")])
        ui.menu("Reports", [("5", "Reports")])
        print()
        print(f"{ui.FG['blue']}6.{ui.RESET} Save & Exit")
        ui.line()

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            um.register_user()
        elif choice == "2":
            um.login_user()
        elif choice == "3":
            um.logout_user()
        elif choice == "4":
            tm.transaction_menu()
        elif choice == "5":
            rm.reports_menu()
        elif choice == "6":
            ui.status_ok("Saving data and exiting... Goodbye.")
            datasets = {
                "users": um.get_users_data(),
                "transactions": tm.get_transactions_data(),
            }
            save_all(datasets)
            break
        else:
            ui.status_warn("Invalid choice. Please enter a number from 1–6.")

if __name__ == "__main__":
    main_menu()

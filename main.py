# main.py
# Orchestrates menus and one-shot save-all on exit (with backups).

import user_manager as um
import transaction_manager as tm
import report_manager as rm
from data_manager import save_all

def main_menu():
    while True:
        print("\n========== Personal Finance Manager ==========")
        cu = um.get_current_user()
        if cu:
            print(f"Logged in as: {cu['username']} ({cu['currency']})")
        else:
            print("Not logged in")

        print("\n--- User ---")
        print("1. Register")
        print("2. Login")
        print("3. Logout")

        print("\n--- Transactions ---")
        print("4. Manage Transactions")

        print("\n--- Reports ---")
        print("5. Reports")

        print("\n6. Save & Exit")
        print("==============================================")

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
            print("Saving data and exiting... Goodbye.")
            # Centralized save with backups
            datasets = {
                "users": um.get_users_data(),
                "transactions": tm.get_transactions_data(),
            }
            save_all(datasets)
            break
        else:
            print("Invalid choice. Please enter a number from 1–6.")

if __name__ == "__main__":
    main_menu()

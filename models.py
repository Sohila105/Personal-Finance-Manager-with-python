import uuid                                   # Imports the uuid module to generate unique IDs.
from datetime import datetime, date           # Imports datetime to timestamp when a user is created.

class User:                                   # Defines a new class named 'User'.
    def __init__(self, name, password, currency="USD"):  # Constructor: runs when you create a User().
        self.user_id = str(uuid.uuid4())      # Creates a unique ID (UUID v4) and stores it as a string.
        self.name = name                      # Saves the user's name as given.
        self.password = password              # Saves the password exactly as provided (plain text for now).
        self.currency = currency              # Saves preferred currency, defaulting to "USD" if not passed.
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                              # Records the current local time as a formatted string, e.g. "2025-10-21 09:15:03".

    def to_dict(self):                        # Method to convert the User object into a plain dictionary.
        return {
            "user_id": self.user_id,          # Includes the unique ID.
            "name": self.name,                # Includes the name.
            "password": self.password,        # Includes the password (still plain text here).
            "currency": self.currency,        # Includes the currency code.
            "created_at": self.created_at     # Includes the creation timestamp string.
        }

    @classmethod                              # Declares the next method is bound to the class, not an instance.
    def from_dict(cls, data):                 # Alternative constructor: build a User from a dictionary.
        user = cls(
            name=data["name"],                # Reads 'name' from the dict (must exist).
            password=data["password"],        # Reads 'password' from the dict (must exist).
            currency=data.get("currency", "USD")  # Reads 'currency' or falls back to "USD" if missing.
        )
        user.user_id = data.get("user_id", str(uuid.uuid4()))
                                              # If the dict has a user_id, use it; otherwise generate a new one.
        user.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                              # If the dict has created_at, use it; otherwise set to now.
        return user                           # Returns the reconstructed User instance.


class Transaction:
    def __init__(
        self,
        user_id,
        txn_type,           # "income" or "expense"
        amount,             # number (float or int)
        category,           # e.g., "Food", "Salary"
        date_str=None,      # "YYYY-MM-DD" (optional; defaults to today)
        description="",     # optional
    ):
        # Basic required fields
        if not user_id:
            raise ValueError("user_id is required.")
        t = (txn_type or "").lower().strip()
        if t not in ("income", "expense"):
            raise ValueError("txn_type must be 'income' or 'expense'.")
        if amount is None:
            raise ValueError("amount is required.")
        if not category or not str(category).strip():
            raise ValueError("category is required.")

        self.transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        self.user_id = user_id
        self.type = t
        self.amount = float(amount)  # keep it simple for now
        self.category = str(category).strip()
        self.date = date_str or date.today().isoformat()  # "YYYY-MM-DD"
        self.description = str(description)

        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "type": self.type,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        txn = cls(
            user_id=data["user_id"],
            txn_type=data["type"],
            amount=data["amount"],
            category=data["category"],
            date_str=data.get("date"),
            description=data.get("description", ""),
        )
        # Keep original IDs/timestamps if present
        txn.transaction_id = data.get("transaction_id", txn.transaction_id)
        txn.created_at = data.get("created_at", txn.created_at)
        txn.updated_at = data.get("updated_at", txn.updated_at)
        return txn

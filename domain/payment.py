"""
Payment class - represents money received from a student against a specific bill.
"""
from datetime import datetime
from domain.receipt import Receipt


# Allowed payment methods (matches the database CHECK constraint)
VALID_METHODS = ("CASH", "BANK_TRANSFER", "MOBILE_MONEY", "CHEQUE")


class Payment:
    def __init__(self, payment_id, bill, amount, method, recorded_by,
                 payment_date=None, is_reversed=False):
        # Validation
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        if method not in VALID_METHODS:
            raise ValueError(f"Invalid payment method: {method}")

        self.payment_id = payment_id
        self.bill = bill                # a Bill object
        self.amount = amount
        self.method = method
        self.recorded_by = recorded_by  # a User object
        self.payment_date = payment_date if payment_date else datetime.now().isoformat()
        self.is_reversed = is_reversed

    def mark_as_reversed(self):
        """Flag this payment as reversed.
        Used when a Reversal is executed against it."""
        self.is_reversed = True

    def generate_receipt(self, receipt_id):
        """Create a Receipt object for this payment."""
        return Receipt(receipt_id, self)

    def __repr__(self):
        reversed_tag = " [REVERSED]" if self.is_reversed else ""
        return f"Payment({self.payment_id}, {self.amount}, {self.method}{reversed_tag})"
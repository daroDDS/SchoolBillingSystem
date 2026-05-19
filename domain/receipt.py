"""
Receipt class - proof of payment given to the student.
"""
from datetime import datetime


class Receipt:
    def __init__(self, receipt_id, payment, issue_date=None, is_cancelled=False):
        self.receipt_id = receipt_id
        self.payment = payment  # a Payment object
        self.issue_date = issue_date if issue_date else datetime.now().isoformat()
        self.is_cancelled = is_cancelled

    def cancel(self):
        """Cancel this receipt (used when the related payment is reversed)."""
        self.is_cancelled = True

    def print_receipt(self):
        """Return a printable text version of the receipt."""
        status = " (CANCELLED)" if self.is_cancelled else ""
        return (
            f"RECEIPT #{self.receipt_id}{status}\n"
            f"Date: {self.issue_date}\n"
            f"Payment amount: {self.payment.amount}\n"
        )

    def __repr__(self):
        return f"Receipt({self.receipt_id}, cancelled={self.is_cancelled})"
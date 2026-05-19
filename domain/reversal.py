"""
Reversal class - cancels the financial effect of a wrong payment.
Keeps the history complete (no deletion).
"""
from datetime import datetime


class Reversal:
    def __init__(self, reversal_id, original_payment, reason, performed_by,
                 reversal_date=None):
        self.reversal_id = reversal_id
        self.original_payment = original_payment  # a Payment object
        self.reason = reason
        self.performed_by = performed_by  # a User object
        self.reversal_date = reversal_date if reversal_date else datetime.now().isoformat()

    def execute(self):
        """Apply the effect of the reversal.
        Marks the original payment as reversed."""
        self.original_payment.is_reversed = True

    def __repr__(self):
        return f"Reversal({self.reversal_id}, payment={self.original_payment.payment_id})"
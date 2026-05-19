"""
Bill class with the State pattern.

A Bill goes through 4 states: UNPAID, PARTIALLY_PAID, PAID, CANCELLED.
Each state defines its own behavior for add_payment, reverse_payment, cancel.

This file contains:
- BillState (abstract base class)
- 4 concrete state classes
- Bill (the main class that delegates to its current state)
"""
from datetime import datetime


# Status constants (match the database CHECK constraint)
STATUS_UNPAID = "UNPAID"
STATUS_PARTIALLY_PAID = "PARTIALLY_PAID"
STATUS_PAID = "PAID"
STATUS_CANCELLED = "CANCELLED"


# ============================================
# Abstract base state
# ============================================
class BillState:
    """Defines what every state must support.
    Each method takes the Bill object as the first argument
    so the state can change the Bill if needed."""

    @property
    def name(self):
        """Return the status name as a string."""
        raise NotImplementedError

    def add_payment(self, bill, amount):
        raise NotImplementedError

    def reverse_payment(self, bill, payment_amount):
        raise NotImplementedError

    def cancel(self, bill):
        raise NotImplementedError


# ============================================
# State 1: UNPAID
# ============================================
class UnpaidState(BillState):

    @property
    def name(self):
        return STATUS_UNPAID

    def add_payment(self, bill, amount):
        bill.amount_paid += amount
        bill.balance = bill.total_amount - bill.amount_paid
        if bill.balance == 0:
            bill.set_state(PaidState())
        else:
            bill.set_state(PartiallyPaidState())

    def reverse_payment(self, bill, payment_amount):
        raise Exception("Cannot reverse a payment on an unpaid bill")

    def cancel(self, bill):
        bill.set_state(CancelledState())


# ============================================
# State 2: PARTIALLY_PAID
# ============================================
class PartiallyPaidState(BillState):

    @property
    def name(self):
        return STATUS_PARTIALLY_PAID

    def add_payment(self, bill, amount):
        bill.amount_paid += amount
        bill.balance = bill.total_amount - bill.amount_paid
        if bill.balance == 0:
            bill.set_state(PaidState())
        # otherwise stays PARTIALLY_PAID (self-transition)

    def reverse_payment(self, bill, payment_amount):
        bill.amount_paid -= payment_amount
        bill.balance = bill.total_amount - bill.amount_paid
        if bill.amount_paid == 0:
            bill.set_state(UnpaidState())
        # otherwise stays PARTIALLY_PAID

    def cancel(self, bill):
        bill.set_state(CancelledState())


# ============================================
# State 3: PAID
# ============================================
class PaidState(BillState):

    @property
    def name(self):
        return STATUS_PAID

    def add_payment(self, bill, amount):
        raise Exception("Bill is already fully paid")

    def reverse_payment(self, bill, payment_amount):
        bill.amount_paid -= payment_amount
        bill.balance = bill.total_amount - bill.amount_paid
        if bill.amount_paid == 0:
            bill.set_state(UnpaidState())
        else:
            bill.set_state(PartiallyPaidState())

    def cancel(self, bill):
        raise Exception("Cannot cancel a fully paid bill")


# ============================================
# State 4: CANCELLED
# ============================================
class CancelledState(BillState):

    @property
    def name(self):
        return STATUS_CANCELLED

    def add_payment(self, bill, amount):
        raise Exception("Bill is cancelled")

    def reverse_payment(self, bill, payment_amount):
        raise Exception("Bill is cancelled")

    def cancel(self, bill):
        raise Exception("Bill is already cancelled")


# ============================================
# The Bill class
# ============================================
class Bill:
    """Represents the amount a student must pay.
    Uses the State pattern to manage its lifecycle."""

    def __init__(self, bill_id, billing_profile, fee_structure,
                 original_amount, total_amount,
                 issue_date=None, due_date=None,
                 discount_amount=0, amount_paid=0, status=None):
        self.bill_id = bill_id
        self.billing_profile = billing_profile  # a BillingProfile object
        self.fee_structure = fee_structure      # a FeeStructure object
        self.original_amount = original_amount
        self.discount_amount = discount_amount
        self.total_amount = total_amount        # = original - discount
        self.amount_paid = amount_paid
        self.balance = total_amount - amount_paid
        self.issue_date = issue_date if issue_date else datetime.now().isoformat()
        self.due_date = due_date

        # Set the initial state based on the current data
        # (important when loading from the database later)
        if status == STATUS_PAID:
            self._state = PaidState()
        elif status == STATUS_PARTIALLY_PAID:
            self._state = PartiallyPaidState()
        elif status == STATUS_CANCELLED:
            self._state = CancelledState()
        else:
            self._state = UnpaidState()

    # ---------- State delegation ----------
    def set_state(self, new_state):
        """Change the current state. Called by the state objects themselves."""
        self._state = new_state

    @property
    def status(self):
        """Return the current status as a string."""
        return self._state.name

    def add_payment(self, amount):
        """Apply a payment. The state decides what happens."""
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        if amount > self.balance:
            raise ValueError(
                f"Payment ({amount}) is greater than remaining balance ({self.balance})"
            )
        self._state.add_payment(self, amount)

    def reverse_payment(self, payment_amount):
        """Undo a payment. The state decides what happens."""
        self._state.reverse_payment(self, payment_amount)

    def cancel(self):
        """Cancel this bill. The state decides if it's allowed."""
        self._state.cancel(self)

    # ---------- Business helpers ----------
    def apply_discount(self, discount_amount):
        """Apply a discount and recalculate the totals.
        If the discount brings the balance to zero (e.g. full waiver),
        the bill is automatically marked as PAID."""
        if self.status != STATUS_UNPAID:
            raise Exception("Discount can only be applied to an unpaid bill")
        self.discount_amount = discount_amount
        self.total_amount = self.original_amount - discount_amount
        self.balance = self.total_amount - self.amount_paid

        # If the discount covers the entire bill, mark it as PAID
        if self.balance == 0:
            self.set_state(PaidState())

    def is_overdue(self):
        """Return True if the due date has passed and the bill is not fully paid."""
        if self.due_date is None:
            return False
        today = datetime.now().date().isoformat()
        return self.due_date < today and self.status in (STATUS_UNPAID, STATUS_PARTIALLY_PAID)

    def __repr__(self):
        return f"Bill({self.bill_id}, balance={self.balance}, status={self.status})"
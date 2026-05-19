"""
Report class - generates summary reports for finance staff.

There are 4 report types:
  - COLLECTED:    total money collected in a date range
  - OUTSTANDING:  total money still owed (unpaid balances)
  - OVERDUE:      bills past their due date
  - DAILY:        all payments recorded on a specific day
"""
from datetime import datetime


# Allowed report types (matches the database CHECK constraint)
VALID_TYPES = ("COLLECTED", "OUTSTANDING", "OVERDUE", "DAILY")


class Report:
    def __init__(self, report_id, report_type, from_date, to_date,
                 generated_by, generated_at=None):
        # Validation
        if report_type not in VALID_TYPES:
            raise ValueError(f"Invalid report type: {report_type}")

        self.report_id = report_id
        self.report_type = report_type
        self.from_date = from_date              # ISO date string, e.g. "2026-01-01"
        self.to_date = to_date
        self.generated_by = generated_by        # a User object
        self.generated_at = generated_at if generated_at else datetime.now().isoformat()

        # The actual data of the report, filled in by generate()
        self.data = None

    # ---------- Generation ----------
    def generate(self, bills, payments):
        """Compute the report data from the given lists of bills and payments.

        Note: in the real prototype, the controller will pass in the right
        lists from the repositories. The class itself doesn't talk to the DB.
        """
        if self.report_type == "COLLECTED":
            self.data = self._collected_report(payments)
        elif self.report_type == "OUTSTANDING":
            self.data = self._outstanding_report(bills)
        elif self.report_type == "OVERDUE":
            self.data = self._overdue_report(bills)
        elif self.report_type == "DAILY":
            self.data = self._daily_report(payments)
        return self.data

    # ---------- Private helpers (one per report type) ----------
    def _collected_report(self, payments):
        """Sum the amount of all non-reversed payments in the date range."""
        in_range = [
            p for p in payments
            if not p.is_reversed and self.from_date <= p.payment_date[:10] <= self.to_date
        ]
        total = sum(p.amount for p in in_range)
        return {
            "type": "COLLECTED",
            "from_date": self.from_date,
            "to_date": self.to_date,
            "total": total,
            "count": len(in_range),
        }

    def _outstanding_report(self, bills):
        """Sum the balance of bills that are not fully paid."""
        unpaid_bills = [
            b for b in bills if b.status in ("UNPAID", "PARTIALLY_PAID")
        ]
        total = sum(b.balance for b in unpaid_bills)
        return {
            "type": "OUTSTANDING",
            "total_outstanding": total,
            "count": len(unpaid_bills),
        }

    def _overdue_report(self, bills):
        """Return all bills that are overdue."""
        overdue = [b for b in bills if b.is_overdue()]
        total = sum(b.balance for b in overdue)
        return {
            "type": "OVERDUE",
            "total_overdue": total,
            "count": len(overdue),
            "bills": [b.bill_id for b in overdue],
        }

    def _daily_report(self, payments):
        """Return all payments recorded on a specific day (from_date)."""
        same_day = [
            p for p in payments
            if not p.is_reversed and p.payment_date[:10] == self.from_date
        ]
        total = sum(p.amount for p in same_day)
        return {
            "type": "DAILY",
            "date": self.from_date,
            "total": total,
            "count": len(same_day),
            "payment_ids": [p.payment_id for p in same_day],
        }

    def __repr__(self):
        return f"Report({self.report_id}, {self.report_type}, {self.from_date} to {self.to_date})"
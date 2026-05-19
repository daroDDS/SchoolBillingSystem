"""
Repository for the Bill class.
Includes special queries: find overdue, find unpaid.
"""
from repositories.database import get_connection
from repositories.billing_profile_repository import BillingProfileRepository
from repositories.fee_structure_repository import FeeStructureRepository
from domain.bill import Bill


class BillRepository:

    def __init__(self):
        self.profile_repository = BillingProfileRepository()
        self.fee_structure_repository = FeeStructureRepository()

    # ---------- Save / Update ----------
    def save(self, bill):
        """Insert a new bill OR update an existing one."""
        connection = get_connection()
        cursor = connection.cursor()

        if bill.bill_id is None:
            # New bill -> INSERT
            cursor.execute(
                """INSERT INTO bill
                   (profile_id, structure_id, original_amount, discount_amount,
                    total_amount, amount_paid, balance, status,
                    issue_date, due_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    bill.billing_profile.profile_id,
                    bill.fee_structure.structure_id,
                    bill.original_amount,
                    bill.discount_amount,
                    bill.total_amount,
                    bill.amount_paid,
                    bill.balance,
                    bill.status,
                    bill.issue_date,
                    bill.due_date,
                )
            )
            bill.bill_id = cursor.lastrowid
        else:
            # Existing bill -> UPDATE the fields that can change
            cursor.execute(
                """UPDATE bill
                   SET discount_amount = ?, total_amount = ?,
                       amount_paid = ?, balance = ?, status = ?
                   WHERE bill_id = ?""",
                (
                    bill.discount_amount,
                    bill.total_amount,
                    bill.amount_paid,
                    bill.balance,
                    bill.status,
                    bill.bill_id,
                )
            )

        connection.commit()
        connection.close()
        return bill

    # ---------- Find ----------
    def find_by_id(self, bill_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bill WHERE bill_id = ?", (bill_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_bill(row)

    def find_by_student(self, student_id):
        """Return all bills for a given student."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """SELECT b.* FROM bill b
               JOIN billing_profile bp ON b.profile_id = bp.profile_id
               WHERE bp.student_id = ?
               ORDER BY b.issue_date DESC""",
            (student_id,)
        )
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_bill(row) for row in rows]

    def find_unpaid(self):
        """Return all bills that are not fully paid."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """SELECT * FROM bill
               WHERE status IN ('UNPAID', 'PARTIALLY_PAID')
               ORDER BY due_date"""
        )
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_bill(row) for row in rows]

    def find_overdue(self):
        """Return bills past their due date and not fully paid."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """SELECT * FROM bill
               WHERE due_date < DATE('now')
                 AND status IN ('UNPAID', 'PARTIALLY_PAID')
               ORDER BY due_date"""
        )
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_bill(row) for row in rows]

    def find_all(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bill ORDER BY issue_date DESC")
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_bill(row) for row in rows]

    # ---------- Helper ----------
    def _row_to_bill(self, row):
        profile = self.profile_repository.find_by_id(row["profile_id"])
        structure = self.fee_structure_repository.find_by_id(row["structure_id"])
        return Bill(
            bill_id=row["bill_id"],
            billing_profile=profile,
            fee_structure=structure,
            original_amount=row["original_amount"],
            total_amount=row["total_amount"],
            discount_amount=row["discount_amount"],
            amount_paid=row["amount_paid"],
            issue_date=row["issue_date"],
            due_date=row["due_date"],
            status=row["status"],  # important! brings back the right state
        )
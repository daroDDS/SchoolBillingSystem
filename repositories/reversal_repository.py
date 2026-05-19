"""
Repository for the Reversal class.
"""
from repositories.database import get_connection
from repositories.payment_repository import PaymentRepository
from repositories.user_repository import UserRepository
from domain.reversal import Reversal


class ReversalRepository:

    def __init__(self):
        self.payment_repository = PaymentRepository()
        self.user_repository = UserRepository()

    def save(self, reversal):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO reversal
               (original_payment_id, reason, reversal_date, performed_by)
               VALUES (?, ?, ?, ?)""",
            (
                reversal.original_payment.payment_id,
                reversal.reason,
                reversal.reversal_date,
                reversal.performed_by.user_id,
            )
        )
        reversal.reversal_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return reversal

    def find_by_id(self, reversal_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reversal WHERE reversal_id = ?", (reversal_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_reversal(row)

    def find_by_payment(self, payment_id):
        """A payment has at most one reversal."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM reversal WHERE original_payment_id = ?",
            (payment_id,)
        )
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_reversal(row)

    def find_all(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reversal ORDER BY reversal_date DESC")
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_reversal(row) for row in rows]

    def _row_to_reversal(self, row):
        payment = self.payment_repository.find_by_id(row["original_payment_id"])
        user = self.user_repository.find_by_id(row["performed_by"])
        return Reversal(
            reversal_id=row["reversal_id"],
            original_payment=payment,
            reason=row["reason"],
            performed_by=user,
            reversal_date=row["reversal_date"],
        )
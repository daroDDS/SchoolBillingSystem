"""
Repository for the Receipt class.
"""
from repositories.database import get_connection
from repositories.payment_repository import PaymentRepository
from domain.receipt import Receipt


class ReceiptRepository:

    def __init__(self):
        self.payment_repository = PaymentRepository()

    def save(self, receipt):
        connection = get_connection()
        cursor = connection.cursor()

        if receipt.receipt_id is None:
            cursor.execute(
                """INSERT INTO receipt (payment_id, issue_date, is_cancelled)
                   VALUES (?, ?, ?)""",
                (
                    receipt.payment.payment_id,
                    receipt.issue_date,
                    1 if receipt.is_cancelled else 0,
                )
            )
            receipt.receipt_id = cursor.lastrowid
        else:
            # Only is_cancelled can change after creation
            cursor.execute(
                "UPDATE receipt SET is_cancelled = ? WHERE receipt_id = ?",
                (1 if receipt.is_cancelled else 0, receipt.receipt_id)
            )

        connection.commit()
        connection.close()
        return receipt

    def find_by_id(self, receipt_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM receipt WHERE receipt_id = ?", (receipt_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_receipt(row)

    def find_by_payment(self, payment_id):
        """A payment has at most one receipt."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM receipt WHERE payment_id = ?", (payment_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_receipt(row)

    def _row_to_receipt(self, row):
        payment = self.payment_repository.find_by_id(row["payment_id"])
        return Receipt(
            receipt_id=row["receipt_id"],
            payment=payment,
            issue_date=row["issue_date"],
            is_cancelled=bool(row["is_cancelled"]),
        )
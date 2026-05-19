"""
Repository for the Payment class.
"""
from repositories.database import get_connection
from repositories.bill_repository import BillRepository
from repositories.user_repository import UserRepository
from domain.payment import Payment


class PaymentRepository:

    def __init__(self):
        self.bill_repository = BillRepository()
        self.user_repository = UserRepository()

    # ---------- Save / Update ----------
    def save(self, payment):
        connection = get_connection()
        cursor = connection.cursor()

        if payment.payment_id is None:
            cursor.execute(
                """INSERT INTO payment
                   (bill_id, amount, payment_date, method, is_reversed, recorded_by)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    payment.bill.bill_id,
                    payment.amount,
                    payment.payment_date,
                    payment.method,
                    1 if payment.is_reversed else 0,
                    payment.recorded_by.user_id,
                )
            )
            payment.payment_id = cursor.lastrowid
        else:
            # Only is_reversed can change after creation
            cursor.execute(
                "UPDATE payment SET is_reversed = ? WHERE payment_id = ?",
                (1 if payment.is_reversed else 0, payment.payment_id)
            )

        connection.commit()
        connection.close()
        return payment

    # ---------- Find ----------
    def find_by_id(self, payment_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM payment WHERE payment_id = ?", (payment_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_payment(row)

    def find_by_bill(self, bill_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM payment WHERE bill_id = ? ORDER BY payment_date",
            (bill_id,)
        )
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_payment(row) for row in rows]

    def find_by_date(self, date_str):
        """Return payments recorded on a specific day (date_str = 'YYYY-MM-DD')."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """SELECT * FROM payment
               WHERE payment_date LIKE ?
               ORDER BY payment_date""",
            (f"{date_str}%",)
        )
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_payment(row) for row in rows]

    def find_all(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM payment ORDER BY payment_date DESC")
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_payment(row) for row in rows]

    # ---------- Helper ----------
    def _row_to_payment(self, row):
        bill = self.bill_repository.find_by_id(row["bill_id"])
        user = self.user_repository.find_by_id(row["recorded_by"])
        return Payment(
            payment_id=row["payment_id"],
            bill=bill,
            amount=row["amount"],
            method=row["method"],
            recorded_by=user,
            payment_date=row["payment_date"],
            is_reversed=bool(row["is_reversed"]),
        )
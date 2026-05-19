"""
Repository for the Discount class.
Uses DiscountFactory to recreate the right subclass when loading.
"""
from repositories.database import get_connection
from repositories.user_repository import UserRepository
from domain.discount import DiscountFactory


class DiscountRepository:

    def __init__(self):
        self.user_repository = UserRepository()

    def save(self, discount, discount_type, bill_id):
        """We need discount_type explicitly because the Discount object
        doesn't store its type directly (it's the class name)."""
        connection = get_connection()
        cursor = connection.cursor()

        # Pull amount / percentage depending on subclass attributes
        amount = getattr(discount, "amount", 0)
        percentage = getattr(discount, "percentage", 0)

        cursor.execute(
            """INSERT INTO discount
               (bill_id, type, amount, percentage, reason, applied_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                bill_id,
                discount_type,
                amount,
                percentage,
                discount.reason,
                discount.applied_by.user_id,
            )
        )
        discount.discount_id = cursor.lastrowid
        discount.bill_id = bill_id
        connection.commit()
        connection.close()
        return discount

    def find_by_id(self, discount_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM discount WHERE discount_id = ?", (discount_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_discount(row)

    def find_by_bill(self, bill_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM discount WHERE bill_id = ?", (bill_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_discount(row)

    def _row_to_discount(self, row):
        applied_by = self.user_repository.find_by_id(row["applied_by"])
        # Use the factory to rebuild the right subclass
        return DiscountFactory.create(
            discount_type=row["type"],
            discount_id=row["discount_id"],
            reason=row["reason"],
            applied_by=applied_by,
            amount=row["amount"],
            percentage=row["percentage"],
            bill_id=row["bill_id"],
        )
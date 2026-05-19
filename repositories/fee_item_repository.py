"""
Repository for the FeeItem class.
"""
from repositories.database import get_connection
from domain.fee_item import FeeItem


class FeeItemRepository:

    def save(self, fee_item):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO fee_item (name, amount) VALUES (?, ?)",
            (fee_item.name, fee_item.amount)
        )
        fee_item.fee_item_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return fee_item

    def find_by_id(self, fee_item_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM fee_item WHERE fee_item_id = ?", (fee_item_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_fee_item(row)

    def find_all(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM fee_item ORDER BY name")
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_fee_item(row) for row in rows]

    def _row_to_fee_item(self, row):
        return FeeItem(
            fee_item_id=row["fee_item_id"],
            name=row["name"],
            amount=row["amount"],
        )
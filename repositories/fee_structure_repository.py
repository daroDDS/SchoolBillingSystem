"""
Repository for the FeeStructure class.
Uses the junction table fee_structure_item to load/save the list of fee items.
"""
from repositories.database import get_connection
from repositories.fee_item_repository import FeeItemRepository
from domain.fee_structure import FeeStructure


class FeeStructureRepository:

    def __init__(self):
        self.fee_item_repository = FeeItemRepository()

    # ---------- Save ----------
    def save(self, fee_structure):
        """Insert the fee structure AND link its items in the junction table."""
        connection = get_connection()
        cursor = connection.cursor()

        # 1) Insert the fee structure row
        cursor.execute(
            """INSERT INTO fee_structure
               (name, term, target_class, is_approved)
               VALUES (?, ?, ?, ?)""",
            (
                fee_structure.name,
                fee_structure.term,
                fee_structure.target_class,
                1 if fee_structure.is_approved else 0,
            )
        )
        fee_structure.structure_id = cursor.lastrowid

        # 2) Insert one row per fee item in the junction table
        for item in fee_structure.fee_items:
            cursor.execute(
                """INSERT INTO fee_structure_item (structure_id, fee_item_id)
                   VALUES (?, ?)""",
                (fee_structure.structure_id, item.fee_item_id)
            )

        connection.commit()
        connection.close()
        return fee_structure

    # ---------- Approve ----------
    def update_approval(self, structure_id, is_approved):
        """Approve or unapprove a fee structure."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE fee_structure SET is_approved = ? WHERE structure_id = ?",
            (1 if is_approved else 0, structure_id)
        )
        connection.commit()
        connection.close()

    # ---------- Find ----------
    def find_by_id(self, structure_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM fee_structure WHERE structure_id = ?",
            (structure_id,)
        )
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_fee_structure(row)

    def find_all(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM fee_structure ORDER BY term, target_class")
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_fee_structure(row) for row in rows]

    # ---------- Helper ----------
    def _row_to_fee_structure(self, row):
        # First, load the linked fee items via the junction table
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT fee_item_id FROM fee_structure_item WHERE structure_id = ?",
            (row["structure_id"],)
        )
        item_ids = [r["fee_item_id"] for r in cursor.fetchall()]
        connection.close()

        # Load each FeeItem object
        fee_items = [self.fee_item_repository.find_by_id(item_id)
                     for item_id in item_ids]

        # Build the FeeStructure with its items
        return FeeStructure(
            structure_id=row["structure_id"],
            name=row["name"],
            term=row["term"],
            target_class=row["target_class"],
            fee_items=fee_items,
            is_approved=bool(row["is_approved"]),
        )
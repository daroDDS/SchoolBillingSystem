"""
FeeItem class - a single fee charged by the school.
"""


class FeeItem:
    def __init__(self, fee_item_id, name, amount):
        self.fee_item_id = fee_item_id
        self.name = name
        self.amount = amount

    def update_amount(self, new_amount):
        """Update the amount of this fee item."""
        if new_amount < 0:
            raise ValueError("Amount cannot be negative")
        self.amount = new_amount

    def __repr__(self):
        return f"FeeItem({self.fee_item_id}, {self.name}, {self.amount})"
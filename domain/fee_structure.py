"""
FeeStructure class - a group of fee items applied to a class, program, or term.
"""


class FeeStructure:
    def __init__(self, structure_id, name, term, target_class,
                 fee_items=None, is_approved=False):
        self.structure_id = structure_id
        self.name = name
        self.term = term
        self.target_class = target_class
        self.fee_items = fee_items if fee_items is not None else []
        self.is_approved = is_approved

    def add_fee_item(self, item):
        """Add a fee item to this structure."""
        self.fee_items.append(item)

    def remove_fee_item(self, item):
        """Remove a fee item from this structure."""
        if item in self.fee_items:
            self.fee_items.remove(item)

    def approve(self):
        """Mark this fee structure as approved."""
        self.is_approved = True

    def get_total_amount(self):
        """Return the sum of all fee item amounts."""
        return sum(item.amount for item in self.fee_items)

    def __repr__(self):
        return f"FeeStructure({self.structure_id}, {self.name}, total={self.get_total_amount()})"
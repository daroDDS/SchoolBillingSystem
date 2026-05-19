"""
Discount class hierarchy + DiscountFactory.
Demonstrates the Factory Method design pattern (creational).
Each discount type calculates the reduction differently.
"""


# ============================================
# Abstract base class
# ============================================
class Discount:
    """Base class for all discount types.
    Subclasses must override compute_amount()."""

    def __init__(self, discount_id, reason, applied_by, bill_id=None):
        self.discount_id = discount_id
        self.reason = reason
        self.applied_by = applied_by  # a User object
        self.bill_id = bill_id        # which bill it applies to

    def compute_amount(self, original_amount):
        """Calculate the discount amount.
        MUST be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement compute_amount()")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.discount_id}, {self.reason})"


# ============================================
# Concrete subclasses (one per discount type)
# ============================================
class FixedAmountDiscount(Discount):
    """A fixed amount discount, e.g. 50000 FCFA off."""

    def __init__(self, discount_id, reason, applied_by, amount, bill_id=None):
        super().__init__(discount_id, reason, applied_by, bill_id)
        self.amount = amount

    def compute_amount(self, original_amount):
        # Never give more discount than the original amount
        return min(self.amount, original_amount)


class PercentageDiscount(Discount):
    """A percentage discount, e.g. 20% off."""

    def __init__(self, discount_id, reason, applied_by, percentage, bill_id=None):
        super().__init__(discount_id, reason, applied_by, bill_id)
        if percentage < 0 or percentage > 100:
            raise ValueError("Percentage must be between 0 and 100")
        self.percentage = percentage

    def compute_amount(self, original_amount):
        return original_amount * self.percentage / 100


class ScholarshipDiscount(Discount):
    """A scholarship discount: 50% off by default."""

    def __init__(self, discount_id, reason, applied_by, bill_id=None):
        super().__init__(discount_id, reason, applied_by, bill_id)
        self.percentage = 50  # scholarship default

    def compute_amount(self, original_amount):
        return original_amount * self.percentage / 100


class WaiverDiscount(Discount):
    """A full waiver: 100% off."""

    def compute_amount(self, original_amount):
        return original_amount


# ============================================
# Factory class
# ============================================
class DiscountFactory:
    """Creates the right Discount subclass based on the type."""

    @staticmethod
    def create(discount_type, discount_id, reason, applied_by,
               amount=0, percentage=0, bill_id=None):
        """Return a Discount object of the requested type.

        discount_type: 'FIXED_AMOUNT', 'PERCENTAGE', 'SCHOLARSHIP', or 'WAIVER'.
        """
        if discount_type == "FIXED_AMOUNT":
            return FixedAmountDiscount(discount_id, reason, applied_by, amount, bill_id)
        elif discount_type == "PERCENTAGE":
            return PercentageDiscount(discount_id, reason, applied_by, percentage, bill_id)
        elif discount_type == "SCHOLARSHIP":
            return ScholarshipDiscount(discount_id, reason, applied_by, bill_id)
        elif discount_type == "WAIVER":
            return WaiverDiscount(discount_id, reason, applied_by, bill_id=bill_id)
        else:
            raise ValueError(f"Unknown discount type: {discount_type}")
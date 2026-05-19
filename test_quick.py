"""
Full reversal scenario:
- Set up everything
- Record a payment + receipt + log
- Reverse it
- Verify the bill, receipt, payment, and log are all updated correctly
"""
from domain.role import Role
from domain.user import User
from domain.student import Student
from domain.billing_profile import BillingProfile
from domain.fee_item import FeeItem
from domain.fee_structure import FeeStructure
from domain.bill import Bill
from domain.payment import Payment
from domain.receipt import Receipt
from domain.reversal import Reversal
from domain.discount import DiscountFactory

from repositories.role_repository import RoleRepository
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository
from repositories.billing_profile_repository import BillingProfileRepository
from repositories.fee_item_repository import FeeItemRepository
from repositories.fee_structure_repository import FeeStructureRepository
from repositories.bill_repository import BillRepository
from repositories.payment_repository import PaymentRepository
from repositories.receipt_repository import ReceiptRepository
from repositories.reversal_repository import ReversalRepository
from repositories.discount_repository import DiscountRepository
from repositories.audit_log_repository import AuditLogRepository


# Repositories
role_repo = RoleRepository()
user_repo = UserRepository()
student_repo = StudentRepository()
profile_repo = BillingProfileRepository()
fee_item_repo = FeeItemRepository()
fs_repo = FeeStructureRepository()
bill_repo = BillRepository()
payment_repo = PaymentRepository()
receipt_repo = ReceiptRepository()
reversal_repo = ReversalRepository()
discount_repo = DiscountRepository()
audit_repo = AuditLogRepository()


# ============================================
# Set up the world
# ============================================
print("=== Setting up ===")
finance_role = role_repo.save(Role(None, "FinanceStaff", ["record_payment"]))
alice = user_repo.save(User(None, "alice", "hashed", finance_role))
daro = student_repo.save(Student(None, "Daro", "Diop", "daro@school.com", "Senior 1", "CS"))
profile = profile_repo.save(BillingProfile(None, daro, "Spring 2026"))
tuition = fee_item_repo.save(FeeItem(None, "Tuition", 500000))
fs = fs_repo.save(FeeStructure(None, "Senior 1 SP26", "Spring 2026", "Senior 1",
                               fee_items=[tuition], is_approved=True))
print()


# ============================================
# Create a bill, apply a discount
# ============================================
print("=== Create bill + discount ===")
bill = Bill(None, profile, fs, original_amount=500000, total_amount=500000,
            due_date="2026-12-31")
bill = bill_repo.save(bill)

# Apply a 10% discount
discount = DiscountFactory.create("PERCENTAGE", None,
                                   "Sibling discount", alice, percentage=10)
discount_amount = discount.compute_amount(bill.original_amount)
bill.apply_discount(discount_amount)
bill = bill_repo.save(bill)
discount = discount_repo.save(discount, "PERCENTAGE", bill.bill_id)

audit_repo.log_action(alice, "discount applied",
                       f"Bill {bill.bill_id}, amount {discount_amount}")

print(f"  Bill: {bill}")
print(f"  Total after discount: {bill.total_amount}")
print()


# ============================================
# Record a payment + receipt
# ============================================
print("=== Record payment + receipt ===")
bill.add_payment(450000)  # full amount after discount
bill = bill_repo.save(bill)

payment = Payment(None, bill, 450000, "BANK_TRANSFER", alice)
payment = payment_repo.save(payment)

receipt = payment.generate_receipt(receipt_id=None)
receipt = receipt_repo.save(receipt)

audit_repo.log_action(alice, "payment recorded",
                       f"Payment {payment.payment_id} for bill {bill.bill_id}")

print(f"  Bill: {bill}")
print(f"  Payment: {payment}")
print(f"  Receipt: {receipt}")
print()


# ============================================
# Reverse the payment (it was wrong!)
# ============================================
print("=== Reverse the payment ===")
reversal = Reversal(None, payment, "Wrong amount entered", alice)
reversal.execute()  # marks payment as reversed
reversal = reversal_repo.save(reversal)
payment = payment_repo.save(payment)  # save the is_reversed flag

# Update the bill (state pattern)
bill.reverse_payment(payment.amount)
bill = bill_repo.save(bill)

# Cancel the receipt
receipt.cancel()
receipt = receipt_repo.save(receipt)

audit_repo.log_action(alice, "payment reversed",
                       f"Reversal {reversal.reversal_id} for payment {payment.payment_id}")

print(f"  Bill after reversal: {bill}")
print(f"  Payment is_reversed: {payment.is_reversed}")
print(f"  Receipt is_cancelled: {receipt.is_cancelled}")
print(f"  Reversal: {reversal}")
print()


# ============================================
# Reload everything and verify it persisted
# ============================================
print("=== Reload from database ===")
bill_loaded = bill_repo.find_by_id(bill.bill_id)
payment_loaded = payment_repo.find_by_id(payment.payment_id)
receipt_loaded = receipt_repo.find_by_payment(payment.payment_id)
reversal_loaded = reversal_repo.find_by_payment(payment.payment_id)
discount_loaded = discount_repo.find_by_bill(bill.bill_id)

print(f"  Bill: {bill_loaded}")
print(f"  Payment is_reversed: {payment_loaded.is_reversed}")
print(f"  Receipt is_cancelled: {receipt_loaded.is_cancelled}")
print(f"  Reversal: {reversal_loaded}")
print(f"  Discount: {discount_loaded}")
print()


# ============================================
# Check the audit log
# ============================================
print("=== Audit log (most recent first) ===")
logs = audit_repo.find_recent(limit=10)
for log in logs:
    print(f"  {log}")
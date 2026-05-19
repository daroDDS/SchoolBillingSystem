"""
Seeds the database with initial test data:
- 3 roles
- 3 users (admin, mohamed = finance, daro = student)
- 2 students (Daro and Aissata)
- 1 billing profile for Daro
- A few fee items
- 1 approved fee structure
- 1 bill for Daro

Run this once after init_db.py to have data to log in with.
"""
from werkzeug.security import generate_password_hash

from domain.role import Role
from domain.user import User
from domain.student import Student
from domain.billing_profile import BillingProfile
from domain.fee_item import FeeItem
from domain.fee_structure import FeeStructure
from domain.bill import Bill

from repositories.role_repository import RoleRepository
from repositories.user_repository import UserRepository
from repositories.student_repository import StudentRepository
from repositories.billing_profile_repository import BillingProfileRepository
from repositories.fee_item_repository import FeeItemRepository
from repositories.fee_structure_repository import FeeStructureRepository
from repositories.bill_repository import BillRepository


print("Seeding database with initial data...")

# Repositories
role_repo = RoleRepository()
user_repo = UserRepository()
student_repo = StudentRepository()
profile_repo = BillingProfileRepository()
fee_item_repo = FeeItemRepository()
fs_repo = FeeStructureRepository()
bill_repo = BillRepository()


# ============================================
# 1. Roles
# ============================================
admin_role = role_repo.save(Role(
    None, "Administrator",
    ["manage_users", "manage_fee_structures", "view_audit", "view_reports"]
))
finance_role = role_repo.save(Role(
    None, "FinanceStaff",
    ["record_payment", "apply_discount", "reverse_payment", "view_reports"]
))
student_role = role_repo.save(Role(
    None, "Student",
    ["view_own_bills"]
))
print(f"  Created roles: Administrator, FinanceStaff, Student")


# ============================================
# 2. Users (with hashed passwords)
# Password for everyone in this seed = 'password123'
# ============================================
default_password_hash = generate_password_hash("password123")

admin_user = user_repo.save(User(None, "admin", default_password_hash, admin_role))
alice_user = user_repo.save(User(None, "mohamed", default_password_hash, finance_role))
daro_user  = user_repo.save(User(None, "daro",  default_password_hash, student_role))
print(f"  Created users: admin, mohamed, daro  (password: 'password123')")


# ============================================
# 3. Students
# ============================================
daro = student_repo.save(Student(
    None, "Daro", "Dieng", "daro@school.com", "Senior 1", "CS",
    user_id=daro_user.user_id
))
aissa = student_repo.save(Student(
    None, "Aissata", "Sow", "aissa@school.com", "Senior 1", "CS"
))
print(f"  Created students: Daro Dieng, Aissata Sow")


# ============================================
# 4. Billing profile for Daro
# ============================================
daro_profile = profile_repo.save(BillingProfile(None, daro, "Spring 2026"))
print(f"  Created billing profile for Daro (Spring 2026)")


# ============================================
# 5. Fee items
# ============================================
tuition = fee_item_repo.save(FeeItem(None, "Tuition", 500000))
registration = fee_item_repo.save(FeeItem(None, "Registration", 50000))
exam_fee = fee_item_repo.save(FeeItem(None, "Exam Fee", 30000))
library_fee = fee_item_repo.save(FeeItem(None, "Library", 20000))
print(f"  Created 4 fee items")


# ============================================
# 6. Approved fee structure for Senior 1
# ============================================
fs = fs_repo.save(FeeStructure(
    None,
    name="Senior 1 - Spring 2026",
    term="Spring 2026",
    target_class="Senior 1",
    fee_items=[tuition, registration, exam_fee, library_fee],
    is_approved=True,
))
print(f"  Created approved fee structure (total: {fs.get_total_amount()})")


# ============================================
# 7. A bill for Daro
# ============================================
bill = Bill(
    bill_id=None,
    billing_profile=daro_profile,
    fee_structure=fs,
    original_amount=fs.get_total_amount(),
    total_amount=fs.get_total_amount(),
    due_date="2026-04-30",  # already past = overdue for demo
)
bill = bill_repo.save(bill)
print(f"  Created bill for Daro (total: {bill.total_amount}, balance: {bill.balance})")


print("\nDone! You can now log in with:")
print("  - admin / password123    (Administrator)")
print("  - mohamed / password123    (Finance Staff)")
print("  - daro  / password123    (Student)")
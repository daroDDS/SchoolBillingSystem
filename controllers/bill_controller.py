"""
BillController - routes for viewing bills.
"""
from flask import Blueprint, render_template, abort

from controllers.helpers import login_required, role_required, get_current_user
from repositories.bill_repository import BillRepository
from repositories.payment_repository import PaymentRepository
from repositories.discount_repository import DiscountRepository
from repositories.student_repository import StudentRepository


bill_bp = Blueprint("bill", __name__)

bill_repo = BillRepository()
payment_repo = PaymentRepository()
discount_repo = DiscountRepository()
student_repo = StudentRepository()


# ============================================
# Route: /bills - list all bills (staff & admin only)
# ============================================
@bill_bp.route("/bills")
@role_required("Administrator", "FinanceStaff")
def list_bills():
    bills = bill_repo.find_all()
    return render_template("bill_list.html", bills=bills)


# ============================================
# Route: /bills/unpaid - only unpaid/partially paid
# ============================================
@bill_bp.route("/bills/unpaid")
@role_required("Administrator", "FinanceStaff")
def list_unpaid():
    bills = bill_repo.find_unpaid()
    return render_template(
        "bill_list.html",
        bills=bills,
        title="Unpaid Bills",
    )


# ============================================
# Route: /bills/overdue - only overdue
# ============================================
@bill_bp.route("/bills/overdue")
@role_required("Administrator", "FinanceStaff")
def list_overdue():
    bills = bill_repo.find_overdue()
    return render_template(
        "bill_list.html",
        bills=bills,
        title="Overdue Bills",
    )


# ============================================
# Route: /bills/<bill_id> - detail of one bill
# ============================================
@bill_bp.route("/bills/<int:bill_id>")
@login_required
def bill_detail(bill_id):
    bill = bill_repo.find_by_id(bill_id)
    if bill is None:
        abort(404)

    # Permission check: students can only see their own bills
    user = get_current_user()
    if user.role.name == "Student":
        # The Student's user_id must match the student linked to this bill
        bill_student = bill.billing_profile.student
        if bill_student.user_id != user.user_id:
            abort(403)  # forbidden

    # Load payments and discount for this bill
    payments = payment_repo.find_by_bill(bill_id)
    discount = discount_repo.find_by_bill(bill_id)

    return render_template(
        "bill_detail.html",
        bill=bill,
        payments=payments,
        discount=discount,
        user=user,
    )

# ============================================
# Route: /my-bills - student's own bills only
# ============================================
@bill_bp.route("/my-bills")
@role_required("Student")
def my_bills():
    user = get_current_user()

    # Find the Student linked to this user account
    students = student_repo.find_all()
    my_student = None
    for s in students:
        if s.user_id == user.user_id:
            my_student = s
            break

    if my_student is None:
        return render_template("bill_list.html",
                               bills=[],
                               title="My Bills",
                               message="No student profile is linked to your account.")

    # Find this student's bills
    bills = bill_repo.find_by_student(my_student.student_id)
    return render_template("bill_list.html",
                           bills=bills,
                           title="My Bills")
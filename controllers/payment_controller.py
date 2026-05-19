"""
PaymentController - routes for recording payments.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from controllers.helpers import role_required, get_current_user
from repositories.bill_repository import BillRepository
from repositories.payment_repository import PaymentRepository
from repositories.receipt_repository import ReceiptRepository
from repositories.audit_log_repository import AuditLogRepository
from domain.payment import Payment
from repositories.reversal_repository import ReversalRepository
from domain.reversal import Reversal
from repositories.student_repository import StudentRepository


payment_bp = Blueprint("payment", __name__)

bill_repo = BillRepository()
payment_repo = PaymentRepository()
receipt_repo = ReceiptRepository()
audit_repo = AuditLogRepository()
reversal_repo = ReversalRepository()
student_repo = StudentRepository()


# ============================================
# Route: /bills/<bill_id>/pay  (GET = show form, POST = save)
# ============================================
@payment_bp.route("/bills/<int:bill_id>/pay", methods=["GET", "POST"])
@role_required("Administrator", "FinanceStaff")
def record_payment(bill_id):
    bill = bill_repo.find_by_id(bill_id)
    if bill is None:
        abort(404)

    user = get_current_user()

    # GET: just show the form
    if request.method == "GET":
        return render_template("payment_form.html", bill=bill)

    # POST: process the form
    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        flash("Invalid amount.", "error")
        return render_template("payment_form.html", bill=bill)

    method = request.form.get("method", "")

    # ============================================
    # Apply the State pattern!
    # bill.add_payment() will:
    #   1. Validate the amount
    #   2. Let the current state decide what happens
    #   3. Transition to the next state (PARTIALLY_PAID or PAID)
    # ============================================
    try:
        bill.add_payment(amount)
    except Exception as e:
        flash(f"Cannot record payment: {e}", "error")
        return render_template("payment_form.html", bill=bill)

    # Save the bill (with its new status and balance)
    bill = bill_repo.save(bill)

    # Create and save the payment
    try:
        payment = Payment(
            payment_id=None,
            bill=bill,
            amount=amount,
            method=method,
            recorded_by=user,
        )
    except ValueError as e:
        flash(f"Invalid payment: {e}", "error")
        return redirect(url_for("bill.bill_detail", bill_id=bill_id))

    payment = payment_repo.save(payment)

    # Generate the receipt
    receipt = payment.generate_receipt(receipt_id=None)
    receipt = receipt_repo.save(receipt)

    # Log the action
    audit_repo.log_action(
        user,
        "payment recorded",
        f"Payment #{payment.payment_id} of {amount} for bill #{bill_id}"
    )

    flash(f"Payment of {amount:.0f} recorded. Bill is now {bill.status}.", "success")
    return redirect(url_for("payment.receipt_view", payment_id=payment.payment_id))


# ============================================
# Route: /receipts/<payment_id>  (view the receipt)
# ============================================
@payment_bp.route("/receipts/<int:payment_id>")
@role_required("Administrator", "FinanceStaff", "Student")
def receipt_view(payment_id):
    payment = payment_repo.find_by_id(payment_id)
    if payment is None:
        abort(404)

    receipt = receipt_repo.find_by_payment(payment_id)
    if receipt is None:
        flash("No receipt found for this payment.", "error")
        return redirect(url_for("bill.bill_detail", bill_id=payment.bill.bill_id))

    # Student permission check: they can only see their own receipts
    user = get_current_user()
    if user.role.name == "Student":
        bill_student = payment.bill.billing_profile.student
        if bill_student.user_id != user.user_id:
            abort(403)

    return render_template("receipt.html", payment=payment, receipt=receipt)

# ============================================
# Route: /payments/<payment_id>/reverse  (GET = form, POST = save)
# ============================================
@payment_bp.route("/payments/<int:payment_id>/reverse", methods=["GET", "POST"])
@role_required("Administrator", "FinanceStaff")
def reverse_payment(payment_id):
    payment = payment_repo.find_by_id(payment_id)
    if payment is None:
        abort(404)

    # Business rule: cannot reverse an already-reversed payment
    if payment.is_reversed:
        flash("This payment has already been reversed.", "error")
        return redirect(url_for("bill.bill_detail", bill_id=payment.bill.bill_id))

    if request.method == "GET":
        return render_template("reversal_form.html", payment=payment)

    # POST: process the form
    user = get_current_user()
    reason = request.form.get("reason", "").strip()

    if not reason:
        flash("Please provide a reason for the reversal.", "error")
        return render_template("reversal_form.html", payment=payment)

    # ============================================
    # Apply the reversal
    # ============================================
    bill = payment.bill

    # 1. Update the bill: balance goes back up, state may change
    #    (State pattern: PAID -> PARTIALLY_PAID, PARTIALLY_PAID -> UNPAID, etc.)
    try:
        bill.reverse_payment(payment.amount)
    except Exception as e:
        flash(f"Cannot reverse: {e}", "error")
        return render_template("reversal_form.html", payment=payment)

    # 2. Mark the payment as reversed (in memory)
    payment.is_reversed = True

    # 3. Create the Reversal record
    reversal = Reversal(
        reversal_id=None,
        original_payment=payment,
        reason=reason,
        performed_by=user,
    )

    # 4. Cancel the receipt
    receipt = receipt_repo.find_by_payment(payment.payment_id)
    if receipt is not None:
        receipt.cancel()

    # 5. Save everything to the database
    bill = bill_repo.save(bill)
    payment = payment_repo.save(payment)
    reversal = reversal_repo.save(reversal)
    if receipt is not None:
        receipt_repo.save(receipt)

    # 6. Log the action
    audit_repo.log_action(
        user,
        "payment reversed",
        f"Reversal #{reversal.reversal_id} for payment #{payment.payment_id} (reason: {reason})"
    )

    flash(
        f"Payment #{payment.payment_id} reversed. Bill is now {bill.status} with balance {bill.balance:.0f}.",
        "success"
    )
    return redirect(url_for("bill.bill_detail", bill_id=bill.bill_id))

# ============================================
# Route: /my-receipts - student's own receipts
# ============================================
@payment_bp.route("/my-receipts")
@role_required("Student")
def my_receipts():
    user = get_current_user()

    # Find the Student linked to this user account
    students = student_repo.find_all()
    my_student = None
    for s in students:
        if s.user_id == user.user_id:
            my_student = s
            break

    if my_student is None:
        return render_template("my_receipts.html", payments=[], student=None)

    # Find all bills of this student, then all their payments
    bills = bill_repo.find_by_student(my_student.student_id)
    all_payments = []
    for bill in bills:
        payments = payment_repo.find_by_bill(bill.bill_id)
        all_payments.extend(payments)

    return render_template("my_receipts.html",
                           payments=all_payments,
                           student=my_student)
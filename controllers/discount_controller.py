"""
DiscountController - apply or remove a discount from a bill.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from controllers.helpers import role_required, get_current_user
from repositories.bill_repository import BillRepository
from repositories.discount_repository import DiscountRepository
from repositories.audit_log_repository import AuditLogRepository
from domain.discount import DiscountFactory


discount_bp = Blueprint("discount", __name__)

bill_repo = BillRepository()
discount_repo = DiscountRepository()
audit_repo = AuditLogRepository()


# ============================================
# Route: /bills/<bill_id>/discount (GET = form, POST = save)
# ============================================
@discount_bp.route("/bills/<int:bill_id>/discount", methods=["GET", "POST"])
@role_required("Administrator", "FinanceStaff")
def apply_discount(bill_id):
    bill = bill_repo.find_by_id(bill_id)
    if bill is None:
        abort(404)

    # Business rule: only unpaid bills can receive a discount
    if bill.status != "UNPAID":
        flash(f"Cannot apply a discount to a {bill.status} bill.", "error")
        return redirect(url_for("bill.bill_detail", bill_id=bill_id))

    # Business rule: only one discount per bill
    existing = discount_repo.find_by_bill(bill_id)
    if existing is not None:
        flash("This bill already has a discount.", "error")
        return redirect(url_for("bill.bill_detail", bill_id=bill_id))

    if request.method == "GET":
        return render_template("discount_form.html", bill=bill)

    # POST: process the form
    user = get_current_user()
    discount_type = request.form.get("discount_type", "")
    reason = request.form.get("reason", "").strip()

    if not reason:
        flash("Please provide a reason for the discount.", "error")
        return render_template("discount_form.html", bill=bill)

    # Read amount or percentage based on type
    # Hidden fields can send empty strings, so we treat empty as 0.
    def safe_float(value):
        if value is None or value.strip() == "":
            return 0.0
        return float(value)

    try:
        amount = safe_float(request.form.get("amount", ""))
        percentage = safe_float(request.form.get("percentage", ""))
    except ValueError:
        flash("Invalid amount or percentage.", "error")
        return render_template("discount_form.html", bill=bill)

    # ============================================
    # Use the Factory Method to create the right discount
    # ============================================
    try:
        discount = DiscountFactory.create(
            discount_type=discount_type,
            discount_id=None,
            reason=reason,
            applied_by=user,
            amount=amount,
            percentage=percentage,
        )
    except ValueError as e:
        flash(f"Invalid discount: {e}", "error")
        return render_template("discount_form.html", bill=bill)

    # Compute the actual discount amount
    discount_amount = discount.compute_amount(bill.original_amount)

    # Refuse if the discount is too big
    if discount_amount > bill.original_amount:
        flash("Discount cannot be larger than the bill amount.", "error")
        return render_template("discount_form.html", bill=bill)

    # Apply to the bill
    try:
        bill.apply_discount(discount_amount)
    except Exception as e:
        flash(f"Cannot apply discount: {e}", "error")
        return render_template("discount_form.html", bill=bill)

    # Save everything
    bill = bill_repo.save(bill)
    discount = discount_repo.save(discount, discount_type, bill.bill_id)

    audit_repo.log_action(
        user,
        "discount applied",
        f"Discount #{discount.discount_id} of {discount_amount:.0f} on bill #{bill_id} ({reason})"
    )

    flash(f"Discount of {discount_amount:.0f} applied. New balance: {bill.balance:.0f}", "success")
    return redirect(url_for("bill.bill_detail", bill_id=bill_id))
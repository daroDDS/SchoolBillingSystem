"""
ReportController - generate financial reports.
Uses the Report class from the domain to compute the data.
"""
from datetime import date, timedelta

from flask import Blueprint, render_template, request

from controllers.helpers import role_required, get_current_user
from repositories.bill_repository import BillRepository
from repositories.payment_repository import PaymentRepository
from repositories.audit_log_repository import AuditLogRepository
from domain.report import Report


report_bp = Blueprint("report", __name__)

bill_repo = BillRepository()
payment_repo = PaymentRepository()
audit_repo = AuditLogRepository()


# ============================================
# Route: /reports - main reports menu
# ============================================
@report_bp.route("/reports")
@role_required("Administrator", "FinanceStaff")
def reports_home():
    return render_template("report_menu.html")


# ============================================
# Route: /reports/<report_type>
# ============================================
@report_bp.route("/reports/<report_type>", methods=["GET", "POST"])
@role_required("Administrator", "FinanceStaff")
def generate_report(report_type):
    report_type = report_type.upper()

    # Validate the type
    if report_type not in ("COLLECTED", "OUTSTANDING", "OVERDUE", "DAILY"):
        return render_template("report_menu.html",
                               error="Unknown report type.")

    # Default dates
    today = date.today().isoformat()
    last_month = (date.today() - timedelta(days=30)).isoformat()

    # On GET: just show the form with default dates
    if request.method == "GET":
        return render_template(
            "report_view.html",
            report_type=report_type,
            from_date=last_month,
            to_date=today,
            data=None,
        )

    # On POST: generate the report
    from_date = request.form.get("from_date", last_month)
    to_date = request.form.get("to_date", today)

    user = get_current_user()
    report = Report(
        report_id=None,
        report_type=report_type,
        from_date=from_date,
        to_date=to_date,
        generated_by=user,
    )

    # Pull data from repositories and pass to the report
    all_bills = bill_repo.find_all()
    all_payments = payment_repo.find_all()
    data = report.generate(all_bills, all_payments)

    # Log the action
    audit_repo.log_action(
        user,
        "report generated",
        f"{report_type} from {from_date} to {to_date}"
    )

    return render_template(
        "report_view.html",
        report_type=report_type,
        from_date=from_date,
        to_date=to_date,
        data=data,
    )
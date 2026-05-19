"""
AuditController - view the audit log entries.
Admin only.
"""
from flask import Blueprint, render_template, request

from controllers.helpers import role_required
from repositories.audit_log_repository import AuditLogRepository


audit_bp = Blueprint("audit", __name__)

audit_repo = AuditLogRepository()


# ============================================
# Route: /audit-log - view recent audit entries
# ============================================
@audit_bp.route("/audit-log")
@role_required("Administrator")
def view_log():
    # How many entries to show (default 100)
    try:
        limit = int(request.args.get("limit", "100"))
    except ValueError:
        limit = 100

    if limit < 10:
        limit = 10
    if limit > 500:
        limit = 500

    entries = audit_repo.find_recent(limit=limit)

    return render_template("audit_log.html", entries=entries, limit=limit)
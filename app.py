"""
School Fee Payment and Billing System - Main Flask application.
"""
from flask import Flask, redirect, url_for

from controllers.auth_controller import auth_bp
from controllers.bill_controller import bill_bp
from controllers.payment_controller import payment_bp
from controllers.discount_controller import discount_bp
from controllers.report_controller import report_bp
from controllers.audit_controller import audit_bp


app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"

app.register_blueprint(auth_bp)
app.register_blueprint(bill_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(discount_bp)
app.register_blueprint(report_bp)
app.register_blueprint(audit_bp)


@app.route("/")
def home():
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
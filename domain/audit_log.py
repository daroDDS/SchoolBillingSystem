"""
AuditLog class - records important actions in the system for traceability.
"""
from datetime import datetime


class AuditLog:
    def __init__(self, log_id, user, action, details=None, timestamp=None):
        self.log_id = log_id
        self.user = user  # a User object
        self.action = action  # e.g. "payment recorded", "payment reversed"
        self.details = details
        self.timestamp = timestamp if timestamp else datetime.now().isoformat()

    def __repr__(self):
        return f"AuditLog({self.log_id}, {self.action}, by {self.user.username})"
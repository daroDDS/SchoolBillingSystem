"""
Role class - defines what a user can do.
Roles: Administrator, FinanceStaff, Student.
"""


class Role:
    def __init__(self, role_id, name, permissions):
        self.role_id = role_id
        self.name = name
        self.permissions = permissions  # list of strings, e.g. ["record_payment", "view_reports"]

    def can_do(self, action):
        """Return True if this role is allowed to perform the action."""
        return action in self.permissions

    def __repr__(self):
        return f"Role({self.role_id}, {self.name})"
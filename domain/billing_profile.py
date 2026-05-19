"""
BillingProfile class - financial profile of a student for a specific term.
"""


class BillingProfile:
    def __init__(self, profile_id, student, term, is_active=True):
        self.profile_id = profile_id
        self.student = student  # a Student object
        self.term = term
        self.is_active = is_active

    def activate(self):
        """Activate this billing profile."""
        self.is_active = True

    def deactivate(self):
        """Deactivate this billing profile."""
        self.is_active = False

    def __repr__(self):
        return f"BillingProfile({self.profile_id}, {self.student.get_full_name()}, {self.term})"
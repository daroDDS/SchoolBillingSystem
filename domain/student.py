"""
Student class - represents a person enrolled in the school.
Matches the design class diagram.
"""


class Student:
    def __init__(self, student_id, first_name, last_name, email,
                 student_class, program, user_id=None):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.student_class = student_class
        self.program = program
        self.user_id = user_id  # optional - may be None if no login account

    # ---------- methods from the class diagram ----------

    def get_full_name(self):
        """Return the full name of the student."""
        return f"{self.first_name} {self.last_name}"

    def get_student_id(self):
        return self.student_id

    def get_email(self):
        return self.email

    # ---------- helper for debugging ----------

    def __repr__(self):
        """Nice display when we print the object."""
        return f"Student({self.student_id}, {self.get_full_name()})"
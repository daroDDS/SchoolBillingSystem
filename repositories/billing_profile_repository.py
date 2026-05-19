"""
Repository for the BillingProfile class.
"""
from repositories.database import get_connection
from repositories.student_repository import StudentRepository
from domain.billing_profile import BillingProfile


class BillingProfileRepository:

    def __init__(self):
        self.student_repository = StudentRepository()

    def save(self, profile):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO billing_profile (student_id, term, is_active)
               VALUES (?, ?, ?)""",
            (
                profile.student.student_id,
                profile.term,
                1 if profile.is_active else 0,
            )
        )
        profile.profile_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return profile

    def find_by_id(self, profile_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM billing_profile WHERE profile_id = ?",
            (profile_id,)
        )
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_profile(row)

    def find_by_student(self, student_id):
        """Return all billing profiles for a given student."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM billing_profile WHERE student_id = ?",
            (student_id,)
        )
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_profile(row) for row in rows]

    def _row_to_profile(self, row):
        student = self.student_repository.find_by_id(row["student_id"])
        return BillingProfile(
            profile_id=row["profile_id"],
            student=student,
            term=row["term"],
            is_active=bool(row["is_active"]),
        )
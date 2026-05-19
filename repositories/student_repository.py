"""
Repository for the Student class.
A Student may be linked to a User account (optional).
"""
from repositories.database import get_connection
from repositories.user_repository import UserRepository
from domain.student import Student


class StudentRepository:

    def __init__(self):
        self.user_repository = UserRepository()

    # ---------- Save ----------
    def save(self, student):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO student
               (first_name, last_name, email, student_class, program, user_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                student.first_name,
                student.last_name,
                student.email,
                student.student_class,
                student.program,
                student.user_id,  # may be None
            )
        )
        student.student_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return student

    # ---------- Find ----------
    def find_by_id(self, student_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM student WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_student(row)

    def find_by_email(self, email):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM student WHERE email = ?", (email,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_student(row)

    def find_all(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM student ORDER BY last_name, first_name")
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_student(row) for row in rows]

    # ---------- Helper ----------
    def _row_to_student(self, row):
        return Student(
            student_id=row["student_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            student_class=row["student_class"],
            program=row["program"],
            user_id=row["user_id"],
        )
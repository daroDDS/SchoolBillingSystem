"""
Repository for the User class.
Uses RoleRepository to load the linked Role when fetching a user.
"""
from repositories.database import get_connection
from repositories.role_repository import RoleRepository
from domain.user import User


class UserRepository:

    def __init__(self):
        # We need RoleRepository to load the role for each user
        self.role_repository = RoleRepository()

    # ---------- Save ----------
    def save(self, user):
        """Insert a new user into the database."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO user (username, password_hash, role_id, is_active)
               VALUES (?, ?, ?, ?)""",
            (
                user.username,
                user.password_hash,
                user.role.role_id,           # store just the role_id
                1 if user.is_active else 0,  # SQLite uses 0/1 for booleans
            )
        )
        user.user_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return user

    # ---------- Find ----------
    def find_by_id(self, user_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_user(row)

    def find_by_username(self, username):
        """Used during login."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        row = cursor.fetchone()
        connection.close()
        if row is None:
            return None
        return self._row_to_user(row)

    def find_all(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_user(row) for row in rows]

    # ---------- Helper ----------
    def _row_to_user(self, row):
        # Load the linked Role using its repository
        role = self.role_repository.find_by_id(row["role_id"])
        return User(
            user_id=row["user_id"],
            username=row["username"],
            password_hash=row["password_hash"],
            role=role,
            is_active=bool(row["is_active"]),
        )
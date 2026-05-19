"""
Repository for the Role class.
Hides all SQL for the role table.
"""
from repositories.database import get_connection
from domain.role import Role


class RoleRepository:

    # ---------- Save ----------
    def save(self, role):
        """Insert a new role into the database.
        Returns the role with its new role_id set."""
        connection = get_connection()
        cursor = connection.cursor()
        # We join the permissions list into a comma-separated string for storage
        permissions_str = ",".join(role.permissions)
        cursor.execute(
            "INSERT INTO role (name, permissions) VALUES (?, ?)",
            (role.name, permissions_str)
        )
        role.role_id = cursor.lastrowid  # the new auto-generated ID
        connection.commit()
        connection.close()
        return role

    # ---------- Find ----------
    def find_by_id(self, role_id):
        """Load a role by its ID. Returns None if not found."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM role WHERE role_id = ?",
            (role_id,)
        )
        row = cursor.fetchone()
        connection.close()

        if row is None:
            return None
        return self._row_to_role(row)

    def find_by_name(self, name):
        """Load a role by its name. Returns None if not found."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM role WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        connection.close()

        if row is None:
            return None
        return self._row_to_role(row)

    def find_all(self):
        """Return all roles as a list of Role objects."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM role")
        rows = cursor.fetchall()
        connection.close()

        return [self._row_to_role(row) for row in rows]

    # ---------- Helper ----------
    def _row_to_role(self, row):
        """Convert a database row into a Role object."""
        permissions_list = row["permissions"].split(",") if row["permissions"] else []
        return Role(
            role_id=row["role_id"],
            name=row["name"],
            permissions=permissions_list,
        )
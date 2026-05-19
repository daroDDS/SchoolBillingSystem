"""
User class - represents any user of the system.
Holds login credentials and a role.
"""


class User:
    def __init__(self, user_id, username, password_hash, role, is_active=True):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role  # a Role object
        self.is_active = is_active

    def has_permission(self, action):
        """Return True if the user's role allows this action."""
        return self.is_active and self.role.can_do(action)

    def __repr__(self):
        return f"User({self.user_id}, {self.username}, role={self.role.name})"
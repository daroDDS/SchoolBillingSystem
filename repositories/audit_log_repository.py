"""
Repository for the AuditLog class.
Includes a convenience function 'log_action' to quickly record an action.
"""
from datetime import datetime

from repositories.database import get_connection
from repositories.user_repository import UserRepository
from domain.audit_log import AuditLog


class AuditLogRepository:

    def __init__(self):
        self.user_repository = UserRepository()

    def save(self, log):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO audit_log (user_id, action, timestamp, details)
               VALUES (?, ?, ?, ?)""",
            (
                log.user.user_id,
                log.action,
                log.timestamp,
                log.details,
            )
        )
        log.log_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return log

    def log_action(self, user, action, details=None):
        """Convenience method - record an action in one call."""
        log = AuditLog(
            log_id=None,
            user=user,
            action=action,
            details=details,
        )
        return self.save(log)

    def find_recent(self, limit=50):
        """Return the most recent audit log entries."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_log(row) for row in rows]

    def find_by_user(self, user_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM audit_log WHERE user_id = ? ORDER BY timestamp DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        connection.close()
        return [self._row_to_log(row) for row in rows]

    def _row_to_log(self, row):
        user = self.user_repository.find_by_id(row["user_id"])
        return AuditLog(
            log_id=row["log_id"],
            user=user,
            action=row["action"],
            details=row["details"],
            timestamp=row["timestamp"],
        )
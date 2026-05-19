"""
Database connection helper.
All repositories use this to talk to SQLite.
"""
import sqlite3

DB_FILE = "school_billing.db"


def get_connection():
    """Open a new connection to the SQLite database.
    Foreign keys are enabled (SQLite requires this explicitly)."""
    connection = sqlite3.connect(DB_FILE)
    connection.execute("PRAGMA foreign_keys = ON")
    # Allow reading rows like dictionaries: row["name"] instead of row[1]
    connection.row_factory = sqlite3.Row
    return connection
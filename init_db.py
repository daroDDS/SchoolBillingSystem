"""
Creates the SQLite database from schema.sql.
Run this once at the start, and again whenever you want a fresh database.
"""
import sqlite3
import os

DB_FILE = "school_billing.db"
SCHEMA_FILE = "schema.sql"

# Delete the old database file if it exists, so we start fresh
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Old {DB_FILE} deleted.")

# Read the SQL schema from the file
with open(SCHEMA_FILE, "r") as f:
    schema_sql = f.read()

# Create a new database and run the schema
connection = sqlite3.connect(DB_FILE)
connection.executescript(schema_sql)
connection.commit()
connection.close()

print(f"Database {DB_FILE} created successfully.")
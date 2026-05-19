PRAGMA foreign_keys = ON;

CREATE TABLE role (
    role_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL UNIQUE,
    permissions  TEXT NOT NULL
);

CREATE TABLE user (
    user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username       TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    role_id        INTEGER NOT NULL,
    is_active      INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (role_id) REFERENCES role(role_id)
);

CREATE TABLE student (
    student_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name     TEXT NOT NULL,
    last_name      TEXT NOT NULL,
    email          TEXT UNIQUE,
    student_class  TEXT NOT NULL,
    program        TEXT NOT NULL,
    user_id        INTEGER,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE billing_profile (
    profile_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL,
    term        TEXT NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);

CREATE TABLE fee_item (
    fee_item_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    amount       REAL NOT NULL CHECK (amount >= 0)
);

CREATE TABLE fee_structure (
    structure_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    term          TEXT NOT NULL,
    target_class  TEXT NOT NULL,
    is_approved   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE fee_structure_item (
    structure_id  INTEGER NOT NULL,
    fee_item_id   INTEGER NOT NULL,
    PRIMARY KEY (structure_id, fee_item_id),
    FOREIGN KEY (structure_id) REFERENCES fee_structure(structure_id),
    FOREIGN KEY (fee_item_id)  REFERENCES fee_item(fee_item_id)
);

CREATE TABLE bill (
    bill_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id       INTEGER NOT NULL,
    structure_id     INTEGER NOT NULL,
    original_amount  REAL NOT NULL CHECK (original_amount >= 0),
    discount_amount  REAL NOT NULL DEFAULT 0 CHECK (discount_amount >= 0),
    total_amount     REAL NOT NULL CHECK (total_amount >= 0),
    amount_paid      REAL NOT NULL DEFAULT 0 CHECK (amount_paid >= 0),
    balance          REAL NOT NULL,
    status           TEXT NOT NULL
                     CHECK (status IN ('UNPAID','PARTIALLY_PAID','PAID','CANCELLED')),
    issue_date       TEXT NOT NULL,
    due_date         TEXT NOT NULL,
    FOREIGN KEY (profile_id)   REFERENCES billing_profile(profile_id),
    FOREIGN KEY (structure_id) REFERENCES fee_structure(structure_id)
);

CREATE TABLE payment (
    payment_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id       INTEGER NOT NULL,
    amount        REAL NOT NULL CHECK (amount > 0),
    payment_date  TEXT NOT NULL,
    method        TEXT NOT NULL
                  CHECK (method IN ('CASH','BANK_TRANSFER','MOBILE_MONEY','CHEQUE')),
    is_reversed   INTEGER NOT NULL DEFAULT 0,
    recorded_by   INTEGER NOT NULL,
    FOREIGN KEY (bill_id)     REFERENCES bill(bill_id),
    FOREIGN KEY (recorded_by) REFERENCES user(user_id)
);

CREATE TABLE receipt (
    receipt_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id    INTEGER NOT NULL UNIQUE,
    issue_date    TEXT NOT NULL,
    is_cancelled  INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (payment_id) REFERENCES payment(payment_id)
);

CREATE TABLE reversal (
    reversal_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    original_payment_id  INTEGER NOT NULL UNIQUE,
    reason               TEXT NOT NULL,
    reversal_date        TEXT NOT NULL,
    performed_by         INTEGER NOT NULL,
    FOREIGN KEY (original_payment_id) REFERENCES payment(payment_id),
    FOREIGN KEY (performed_by)        REFERENCES user(user_id)
);

CREATE TABLE discount (
    discount_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id      INTEGER NOT NULL UNIQUE,
    type         TEXT NOT NULL
                 CHECK (type IN ('FIXED_AMOUNT','PERCENTAGE','SCHOLARSHIP','WAIVER')),
    amount       REAL DEFAULT 0 CHECK (amount >= 0),
    percentage   REAL DEFAULT 0 CHECK (percentage >= 0 AND percentage <= 100),
    reason       TEXT NOT NULL,
    applied_by   INTEGER NOT NULL,
    FOREIGN KEY (bill_id)    REFERENCES bill(bill_id),
    FOREIGN KEY (applied_by) REFERENCES user(user_id)
);

CREATE TABLE audit_log (
    log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    action     TEXT NOT NULL,
    timestamp  TEXT NOT NULL,
    details    TEXT,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE report (
    report_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    type          TEXT NOT NULL
                  CHECK (type IN ('COLLECTED','OUTSTANDING','OVERDUE','DAILY')),
    from_date     TEXT NOT NULL,
    to_date       TEXT NOT NULL,
    generated_by  INTEGER NOT NULL,
    generated_at  TEXT NOT NULL,
    FOREIGN KEY (generated_by) REFERENCES user(user_id)
);
import sqlite3

DATABASE_NAME = "data/enquiries.db"


def create_table():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'received',
            category TEXT,
            lead_score INTEGER,
            response_draft TEXT
        )
    """)

    # Existing database-la missing columns add pannum
    existing_columns = [
        row[1] for row in cursor.execute(
            "PRAGMA table_info(enquiries)"
        ).fetchall()
    ]

    for column, datatype in [
        ("category", "TEXT"),
        ("lead_score", "INTEGER"),
        ("response_draft", "TEXT")
    ]:
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE enquiries ADD COLUMN {column} {datatype}"
            )

    connection.commit()
    connection.close()


def save_enquiry(
    customer_name, email, message,
    category=None, lead_score=None, response_draft=None
):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO enquiries
        (customer_name, email, message, category, lead_score, response_draft)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        customer_name, email, message,
        category, lead_score, response_draft
    ))

    connection.commit()
    enquiry_id = cursor.lastrowid
    connection.close()

    return enquiry_id
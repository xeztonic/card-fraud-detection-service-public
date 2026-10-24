import os
import csv
import sqlite3


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "transactions.db")
CSV_PATH = os.path.join(DATA_DIR, "transactions_export.csv")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
   # cursor.execute("DROP TABLE IF EXISTS transactions")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        transaction_amt REAL,
        transaction_dt REAL,

        card1 TEXT,
        card2 TEXT,
        card4 TEXT,

        addr1 TEXT,
        dist1 REAL,

        product_cd TEXT,

        email TEXT,
        customer_email TEXT,

        fraud_probability REAL,
        risk_score REAL,
        risk_category TEXT,
        risk_factors TEXT,

        email_alert_sent INTEGER,
        customer_alert_sent INTEGER,
                   

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    conn.commit()
    conn.close()


def save_transaction(transaction):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (
            transaction_amt,
            transaction_dt,
            card1,
            card2,
            card4,
            addr1,
            dist1,
            product_cd,
            email,
            customer_email,
            fraud_probability,
            risk_score,
            risk_category,
            risk_factors,
            email_alert_sent,
            customer_alert_sent
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction["transaction_amt"],
        transaction["transaction_dt"],
        transaction["card1"],
        transaction["card2"],
        transaction["card4"],
        transaction["addr1"],
        transaction["dist1"],
        transaction["product_cd"],
        transaction["email"],
        transaction["customer_email"],
        transaction["fraud_probability"],
        transaction["risk_score"],
        transaction["risk_category"],
        transaction["risk_factors"],
        int(transaction["email_alert_sent"]),
        int(transaction["customer_alert_sent"])
    ))

    conn.commit()
    conn.close()


def get_transactions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


def clear_transactions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions")

    conn.commit()
    conn.close()


def export_transactions_to_csv():
    transactions = get_transactions()

    fieldnames = [
        "id",
        "transaction_amt",
        "transaction_dt",
        "card1",
        "card2",
        "card4",
        "addr1",
        "dist1",
        "product_cd",
        "email",
        "customer_email",
        "fraud_probability",
        "risk_score",
        "risk_category",
        "email_alert_sent",
        "customer_alert_sent",
        "created_at"
    ]

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(transactions)

    return CSV_PATH


# live chart
def get_recent_transactions(limit=150):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows][::-1]
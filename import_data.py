import sqlite3
import csv

connection = sqlite3.connect("recallguard.db")
cursor = connection.cursor()

# Make sure all required columns exist
existing = [row[1] for row in cursor.execute("PRAGMA table_info(recalls)")]

new_columns = [
    ("category", "TEXT"),
    ("source_month", "TEXT"),
    ("manufacture_date", "TEXT"),
    ("expiry_date", "TEXT"),
    ("reported_by", "TEXT")
]

for column, data_type in new_columns:
    if column not in existing:
        cursor.execute(
            f"ALTER TABLE recalls ADD COLUMN {column} {data_type}"
        )

# Remove old test/previous records
cursor.execute("DELETE FROM recalls")

# Import ONLY June 2025 NSQ data
with open("recallguard_june2025_nsq.csv", "r", encoding="utf-8-sig") as file:

    reader = csv.DictReader(file)
    count = 0

    for row in reader:

        cursor.execute("""
        INSERT INTO recalls
        (
            medicine,
            manufacturer,
            batch,
            reason,
            category,
            source_month,
            manufacture_date,
            expiry_date,
            reported_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["medicine"],
            row["manufacturer"],
            row["batch"],
            row["nsq_result"],
            "NSQ",
            "June 2025",
            row["manufacturing_date"],
            row["expiry_date"],
            row["reported_by"]
        ))

        count += 1

connection.commit()
connection.close()

print(f"✅ Imported {count} June 2025 NSQ records!")
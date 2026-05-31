import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="vehicle_booking",
    autocommit=True
)

cur = conn.cursor(buffered=True)

# Quick sanity check when db.py is run directly
if __name__ == "__main__":
    cur.execute("SELECT DATABASE()")
    print(f"[OK] Connected to: {cur.fetchone()[0]}")
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    print(f"[OK] Tables found: {[t[0] for t in tables]}")
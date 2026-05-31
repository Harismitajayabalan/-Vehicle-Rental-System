from db import conn, cur

# ── Create Tables ──────────────────────────────────────────────
try:
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(100) UNIQUE,
            password VARCHAR(100),
            mobile VARCHAR(15),
            email VARCHAR(100)
        )
    """)
    print("[OK] users table ready")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers(
            customer_id INT PRIMARY KEY AUTO_INCREMENT,
            customer_name VARCHAR(100),
            phone VARCHAR(15)
        )
    """)
    print("[OK] customers table ready")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicles(
            vehicle_id INT PRIMARY KEY AUTO_INCREMENT,
            vehicle_type VARCHAR(20),
            brand VARCHAR(50),
            model VARCHAR(50),
            category VARCHAR(50),
            rent_per_day INT
        )
    """)
    print("[OK] vehicles table ready")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
            booking_id INT PRIMARY KEY AUTO_INCREMENT,
            customer_id INT,
            vehicle_id INT,
            booking_date DATE,
            booking_days INT,
            total_amount INT,
            return_status VARCHAR(20),
            actual_return_date DATE,
            late_fine INT
        )
    """)
    print("[OK] bookings table ready")

    conn.commit()
    print("[OK] All tables committed successfully")
    


except Exception as e:
    conn.rollback()
    print(f"[ERROR] Table creation failed: {e}")
    exit(1)  # Stop here — no point inserting if tables failed


# ── Vehicle Data ───────────────────────────────────────────────
vehicle_data = [
    ("Car","Maruti Suzuki","Swift","5 Seater",5000),
    ("Car","Maruti Suzuki","WagonR","5 Seater",5000),
    ("Car","Maruti Suzuki","Dzire","5 Seater",5000),
    ("Car","Hyundai","Grand i10 Nios","5 Seater",5000),
    ("Car","Hyundai","Aura","5 Seater",5000),
    ("Car","Hyundai","Exter","5 Seater",5000),
    ("Car","Tata","Tiago","5 Seater",5000),
    ("Car","Tata","Punch","5 Seater",5000),
    ("Car","Tata","Nexon","5 Seater",5000),
    ("Car","Honda","Amaze","5 Seater",5000),
    ("Car","Mahindra","XUV 3XO","5 Seater",5000),
    ("Car","Maruti Suzuki","Ertiga","7 Seater",7000),
    ("Car","Mahindra","Scorpio N","7 Seater",7000),
    ("Car","Toyota","Innova Crysta","7 Seater",7000),
    ("Car","Toyota","Fortuner","7 Seater",7000),
    ("Car","Kia","Carens","7 Seater",7000),
    ("Car","Renault","Triber","7 Seater",7000),
    ("Bike","Hero","Splendor Plus 97","Below 150cc",500),
    ("Bike","Honda","Shine 125","Below 150cc",500),
    ("Bike","Yamaha","FZ-S 149","Below 150cc",500),
    ("Bike","Bajaj","Pulsar 150","150cc-250cc",1500),
    ("Bike","Bajaj","Pulsar NS200","150cc-250cc",1500),
    ("Bike","TVS","Apache RTR 160","150cc-250cc",1500),
    ("Bike","TVS","Apache RTR 200","150cc-250cc",1500),
    ("Bike","KTM","Duke 200","Above 250cc",2500),
    ("Bike","KTM","Duke 390","Above 250cc",2500),
    ("Bike","Royal Enfield","Classic 350","Above 250cc",2500),
    ("Bike","Royal Enfield","Bullet 350","Above 250cc",2500),
]

# ── Insert with Duplicate Check + Logging ─────────────────────
inserted = 0
skipped = 0
failed = 0

print(f"\n[INFO] Starting vehicle seeding — {len(vehicle_data)} records to process\n")

for idx, data in enumerate(vehicle_data, start=1):
    vehicle_type, brand, model, category, rent = data
    try:
        # Check for existing record
        cur.execute(
            "SELECT vehicle_id FROM vehicles WHERE brand=%s AND model=%s",
            (brand, model)
        )
        result = cur.fetchone()

        if result:
            print(f"[SKIP] ({idx:02}) {brand} {model} already exists (id={result[0]})")
            skipped += 1
        else:
            cur.execute("""
                INSERT INTO vehicles(vehicle_type, brand, model, category, rent_per_day)
                VALUES(%s, %s, %s, %s, %s)
            """, data)
            conn.commit()  # Commit each insert so failures don't roll back everything
            print(f"[INSERT] ({idx:02}) {brand} {model} — {category} @ ₹{rent}/day ✓")
            inserted += 1

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] ({idx:02}) Failed to insert {brand} {model}: {e}")
        failed += 1

# ── Summary ────────────────────────────────────────────────────
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━
  Seeding Complete
  Inserted : {inserted}
  Skipped  : {skipped}
  Failed   : {failed}
  Total    : {len(vehicle_data)}
━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# ── Verify: Read back from DB ──────────────────────────────────
print("[INFO] Verifying data in vehicles table:\n")
cur.execute("SELECT vehicle_id, vehicle_type, brand, model, category, rent_per_day FROM vehicles")
rows = cur.fetchall()

if not rows:
    print("[WARNING] vehicles table is EMPTY — inserts may have failed!")
else:
    print(f"{'ID':<5} {'Type':<6} {'Brand':<20} {'Model':<20} {'Category':<15} {'Rent/Day':>10}")
    print("─" * 80)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<6} {row[2]:<20} {row[3]:<20} {row[4]:<15} ₹{row[5]:>8}")
    print(f"\n[OK] {len(rows)} vehicle(s) found in table")
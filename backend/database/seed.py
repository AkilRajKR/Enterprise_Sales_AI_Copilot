#!/usr/bin/env python3
"""
Seed script for Enterprise Sales AI Copilot:
- Creates SQLite database schema (sales.db)
- Loads initial seed data from seed_data.sql
- Generates synthetic data using Faker to reach 150 rows per table
- Handles FK constraints and avoids duplicate entries
"""
import sqlite3
import os
import re
import sys
from faker import Faker
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DB_DIR = Path(__file__).parent
DB_PATH = DB_DIR / "sales.db"
SCHEMA_FILE = DB_DIR / "Create_Tables.sql"
INPUT_SEED_FILE = DB_DIR / "seed_data.sql"
TARGET_ROWS = 150

fake = Faker()
random.seed(42)
Faker.seed(42)

def exec_sql_file(conn, path):
    """Execute SQL file with error handling."""
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    try:
        conn.executescript(sql)
        return []
    except Exception as e:
        # Try individual statements and collect errors
        errors = []
        stmts = [s.strip() + ";" for s in sql.split(";") if s.strip()]
        for s in stmts:
            try:
                conn.executescript(s)
            except Exception as ex:
                errors.append((s[:200], str(ex)))
        return errors

def table_count(conn, table):
    """Get row count for a table."""
    try:
        cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0]
    except Exception:
        return 0

def get_ids(conn, table, idcol):
    """Fetch all IDs from a column."""
    try:
        cur = conn.execute(f"SELECT {idcol} FROM {table}")
        return [r[0] for r in cur.fetchall()]
    except Exception:
        return []

def safe_commit(conn):
    """Safely commit transaction."""
    try:
        conn.commit()
    except Exception as e:
        print(f"Warning: Commit error: {e}")

def generate_missing(conn):
    """Generate synthetic data to reach TARGET_ROWS per table."""
    
    def ensure_brands():
        cnt = table_count(conn, "Brands")
        print(f"  Brands: {cnt}/{TARGET_ROWS}", end="")
        while cnt < TARGET_ROWS:
            try:
                name = fake.company()[:50]
                conn.execute("INSERT INTO Brands (brand_name) VALUES (?)", (name,))
                cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_manufacture_plants():
        cnt = table_count(conn, "Manufacture_Plant")
        print(f"  Manufacture_Plant: {cnt}/{TARGET_ROWS}", end="")
        while cnt < TARGET_ROWS:
            try:
                plant = fake.company()[:50]
                ptype = random.choice(["Assembly", "Parts"])
                loc = fake.city()[:100]
                co = random.choice([0, 1])
                conn.execute(
                    "INSERT INTO Manufacture_Plant (plant_name, plant_type, plant_location, company_owned) VALUES (?,?,?,?)",
                    (plant, ptype, loc, co)
                )
                cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_dealers():
        cnt = table_count(conn, "Dealers")
        print(f"  Dealers: {cnt}/{TARGET_ROWS}", end="")
        while cnt < TARGET_ROWS:
            try:
                name = fake.company()[:50]
                addr = fake.address()[:200]
                conn.execute("INSERT INTO Dealers (dealer_name, dealer_address) VALUES (?,?)", (name, addr))
                cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_models():
        cnt = table_count(conn, "Models")
        print(f"  Models: {cnt}/{TARGET_ROWS}", end="")
        brand_ids = get_ids(conn, "Brands", "brand_id")
        if not brand_ids:
            ensure_brands()
            brand_ids = get_ids(conn, "Brands", "brand_id")
        while cnt < TARGET_ROWS:
            try:
                mname = fake.word().capitalize()[:50]
                price = random.randint(15000, 120000)
                brand = random.choice(brand_ids)
                conn.execute(
                    "INSERT INTO Models (model_name, model_base_price, brand_id) VALUES (?,?,?)",
                    (mname, price, brand)
                )
                cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_car_parts():
        cnt = table_count(conn, "Car_Parts")
        print(f"  Car_Parts: {cnt}/{TARGET_ROWS}", end="")
        plant_ids = get_ids(conn, "Manufacture_Plant", "manufacture_plant_id")
        if not plant_ids:
            ensure_manufacture_plants()
            plant_ids = get_ids(conn, "Manufacture_Plant", "manufacture_plant_id")
        while cnt < TARGET_ROWS:
            try:
                part = fake.word().capitalize() + " part"
                plant = random.choice(plant_ids)
                start = fake.date_between(start_date='-10y', end_date='today').isoformat()
                end = None if random.random() < 0.8 else (
                    datetime.fromisoformat(start) + timedelta(days=365*3)
                ).date().isoformat()
                recall = 1 if random.random() < 0.05 else 0
                conn.execute(
                    "INSERT INTO Car_Parts (part_name, manufacture_plant_id, manufacture_start_date, manufacture_end_date, part_recall) VALUES (?,?,?,?,?)",
                    (part[:100], plant, start, end, recall)
                )
                cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_car_options():
        cnt = table_count(conn, "Car_Options")
        print(f"  Car_Options: {cnt}/{TARGET_ROWS}", end="")
        model_ids = get_ids(conn, "Models", "model_id")
        part_ids = get_ids(conn, "Car_Parts", "part_id")
        if not part_ids:
            ensure_car_parts()
            part_ids = get_ids(conn, "Car_Parts", "part_id")
        while cnt < TARGET_ROWS:
            try:
                model = random.choice(model_ids) if model_ids and random.random() < 0.9 else None
                engine = random.choice(part_ids)
                transmission = random.choice(part_ids)
                chassis = random.choice(part_ids)
                premium = random.choice(part_ids) if random.random() < 0.3 else None
                color = random.choice(["Black", "White", "Red", "Blue", "Silver", "Gray", "Beige", "Green"])
                price = random.randint(500, 15000)
                conn.execute(
                    "INSERT INTO Car_Options (model_id, engine_id, transmission_id, chassis_id, premium_sound_id, color, option_set_price) VALUES (?,?,?,?,?,?,?)",
                    (model, engine, transmission, chassis, premium, color, price)
                )
                cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_car_vins():
        cnt = table_count(conn, "Car_Vins")
        print(f"  Car_Vins: {cnt}/{TARGET_ROWS}", end="")
        model_ids = get_ids(conn, "Models", "model_id")
        option_ids = get_ids(conn, "Car_Options", "option_set_id")
        plant_ids = get_ids(conn, "Manufacture_Plant", "manufacture_plant_id")
        while cnt < TARGET_ROWS:
            try:
                model = random.choice(model_ids) if model_ids else 1
                opt = random.choice(option_ids) if option_ids else 1
                mdate = fake.date_between(start_date=datetime(2018, 1, 1).date(), end_date=datetime(2026, 12, 31).date()).isoformat()
                plant = random.choice(plant_ids) if plant_ids else 1
                conn.execute(
                    "INSERT INTO Car_Vins (model_id, option_set_id, manufactured_date, manufactured_plant_id) VALUES (?,?,?,?)",
                    (model, opt, mdate, plant)
                )
                cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_customers():
        cnt = table_count(conn, "Customers")
        print(f"  Customers: {cnt}/{TARGET_ROWS}", end="")
        while cnt < TARGET_ROWS:
            try:
                fn = fake.first_name()[:50]
                ln = fake.last_name()[:50]
                gender = random.choice(["Male", "Female"])
                income = random.randint(20000, 400000)
                birth = fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
                phone = re.sub(r'\D', '', fake.phone_number())[:20]
                email = fake.email()[:128]
                conn.execute(
                    "INSERT INTO Customers (first_name, last_name, gender, household_income, birthdate, phone_number, email) VALUES (?,?,?,?,?,?,?)",
                    (fn, ln, gender, income, birth, phone, email)
                )
                cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_dealer_brand():
        cnt = table_count(conn, "Dealer_Brand")
        print(f"  Dealer_Brand: {cnt}/{TARGET_ROWS}", end="")
        dealer_ids = get_ids(conn, "Dealers", "dealer_id")
        brand_ids = get_ids(conn, "Brands", "brand_id")
        existing = set(conn.execute("SELECT dealer_id, brand_id FROM Dealer_Brand").fetchall())
        while cnt < TARGET_ROWS:
            try:
                d = random.choice(dealer_ids) if dealer_ids else 1
                b = random.choice(brand_ids) if brand_ids else 1
                if (d, b) not in existing:
                    conn.execute("INSERT INTO Dealer_Brand (dealer_id, brand_id) VALUES (?,?)", (d, b))
                    existing.add((d, b))
                    cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    def ensure_customer_ownership():
        cnt = table_count(conn, "Customer_Ownership")
        print(f"  Customer_Ownership: {cnt}/{TARGET_ROWS}", end="")
        customer_ids = get_ids(conn, "Customers", "customer_id")
        vin_ids = get_ids(conn, "Car_Vins", "vin")
        dealer_ids = get_ids(conn, "Dealers", "dealer_id")
        existing = set(conn.execute("SELECT customer_id, vin FROM Customer_Ownership").fetchall())
        while cnt < TARGET_ROWS:
            try:
                c = random.choice(customer_ids) if customer_ids else 1
                v = random.choice(vin_ids) if vin_ids else 1
                if (c, v) not in existing:
                    purchase_date = fake.date_between(start_date=datetime(2018, 1, 1).date(), end_date=datetime(2026, 12, 31).date()).isoformat()
                    price = random.randint(10000, 120000)
                    warantee = None if random.random() < 0.3 else (datetime.fromisoformat(purchase_date) + timedelta(days=365*5)).date().isoformat()
                    dealer = random.choice(dealer_ids) if dealer_ids else 1
                    conn.execute(
                        "INSERT INTO Customer_Ownership (customer_id, vin, purchase_date, purchase_price, warantee_expire_date, dealer_id) VALUES (?,?,?,?,?,?)",
                        (c, v, purchase_date, price, warantee, dealer)
                    )
                    existing.add((c, v))
                    cnt += 1
            except Exception:
                pass
        safe_commit(conn)
        print(f" → {cnt}")

    # Execute in dependency order
    print("\n📊 Generating synthetic data:")
    ensure_brands()
    ensure_manufacture_plants()
    ensure_dealers()
    ensure_models()
    ensure_car_parts()
    ensure_car_options()
    ensure_car_vins()
    ensure_customers()
    ensure_dealer_brand()
    ensure_customer_ownership()

def main():
    # Remove existing DB for fresh start
    if DB_PATH.exists():
        print(f"🗑️  Removing existing {DB_PATH}")
        DB_PATH.unlink()

    print(f"\n✅ Creating SQLite database at {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Enable FK constraints
    conn.execute("PRAGMA foreign_keys = ON")

    # Create schema
    print(f"\n📋 Executing schema from {SCHEMA_FILE}")
    if not SCHEMA_FILE.exists():
        print(f"⚠️  Schema file not found: {SCHEMA_FILE}")
        conn.close()
        return
    
    errors = exec_sql_file(conn, SCHEMA_FILE)
    if errors:
        print(f"⚠️  Schema had {len(errors)} errors (will continue):")
        for s, e in errors[:3]:
            print(f"   - {e[:100]}")

    # Apply seed data
    if INPUT_SEED_FILE.exists():
        print(f"\n📥 Loading seed data from {INPUT_SEED_FILE}")
        seed_errors = exec_sql_file(conn, INPUT_SEED_FILE)
        if seed_errors:
            print(f"⚠️  Seed file had {len(seed_errors)} errors (generating synthetic data to compensate)")
        else:
            print("✅ Seed data loaded successfully")
    else:
        print(f"⚠️  Seed file not found: {INPUT_SEED_FILE}")

    # Show initial counts
    tables = ["Brands", "Manufacture_Plant", "Dealers", "Models", "Car_Parts", 
              "Car_Options", "Car_Vins", "Customers", "Dealer_Brand", "Customer_Ownership"]
    print(f"\n📊 Initial row counts:")
    for t in tables:
        cnt = table_count(conn, t)
        print(f"  {t}: {cnt}")

    # Generate missing rows
    print(f"\n🤖 Filling to {TARGET_ROWS} rows per table...")
    generate_missing(conn)

    # Final counts
    print(f"\n✨ Final row counts:")
    total_rows = 0
    for t in tables:
        cnt = table_count(conn, t)
        total_rows += cnt
        print(f"  {t}: {cnt}")
    
    print(f"\n📊 Total rows across all tables: {total_rows}")
    
    conn.close()
    print(f"\n✅ Database initialized successfully: {DB_PATH}")
    print(f"📈 Database size: {DB_PATH.stat().st_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()

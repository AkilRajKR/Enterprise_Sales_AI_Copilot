"""
database/schema.py — Automotive Sales Database initializer.

This module creates the correct automotive schema and seeds the qa_cache table.
The actual domain data is seeded by seed.py using Create_Tables.sql.

To initialize from scratch:
    python -m database.schema
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tables that must exist for the system to operate (not automotive business tables —
# those come from seed.py / Create_Tables.sql)
_QA_CACHE_DDL = """
CREATE TABLE IF NOT EXISTS qa_cache (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    normalized_question TEXT UNIQUE NOT NULL,
    original_question   TEXT NOT NULL,
    sql_query           TEXT NOT NULL,
    answer              TEXT NOT NULL,
    evidence            TEXT NOT NULL DEFAULT '{}',
    confidence          REAL NOT NULL,
    execution_time_ms   REAL NOT NULL DEFAULT 0,
    token_usage         TEXT NOT NULL DEFAULT '{}',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# Full automotive schema (mirrors Create_Tables.sql so this file is self-contained)
_AUTOMOTIVE_SCHEMA_DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Brands (
    brand_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Manufacture_Plant (
    manufacture_plant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_name           TEXT NOT NULL,
    plant_type           TEXT CHECK(plant_type IN ('Assembly', 'Parts')),
    plant_location       TEXT NOT NULL,
    company_owned        INTEGER DEFAULT 0,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Dealers (
    dealer_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    dealer_name    TEXT NOT NULL,
    dealer_address TEXT NOT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Models (
    model_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name       TEXT NOT NULL,
    model_base_price DECIMAL(10, 2) NOT NULL CHECK(model_base_price > 0),
    brand_id         INTEGER NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES Brands(brand_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Car_Parts (
    part_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    part_name             TEXT NOT NULL,
    manufacture_plant_id  INTEGER NOT NULL,
    manufacture_start_date DATE,
    manufacture_end_date   DATE,
    part_recall           INTEGER DEFAULT 0,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manufacture_plant_id) REFERENCES Manufacture_Plant(manufacture_plant_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Car_Options (
    option_set_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id          INTEGER,
    engine_id         INTEGER NOT NULL,
    transmission_id   INTEGER NOT NULL,
    chassis_id        INTEGER NOT NULL,
    premium_sound_id  INTEGER,
    color             TEXT NOT NULL,
    option_set_price  DECIMAL(10, 2) NOT NULL CHECK(option_set_price > 0),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id)         REFERENCES Models(model_id)      ON DELETE SET NULL,
    FOREIGN KEY (engine_id)        REFERENCES Car_Parts(part_id)    ON DELETE RESTRICT,
    FOREIGN KEY (transmission_id)  REFERENCES Car_Parts(part_id)    ON DELETE RESTRICT,
    FOREIGN KEY (chassis_id)       REFERENCES Car_Parts(part_id)    ON DELETE RESTRICT,
    FOREIGN KEY (premium_sound_id) REFERENCES Car_Parts(part_id)    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Car_Vins (
    vin                  INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id             INTEGER NOT NULL,
    option_set_id        INTEGER NOT NULL,
    manufactured_date    DATE NOT NULL,
    manufactured_plant_id INTEGER NOT NULL,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id)              REFERENCES Models(model_id)           ON DELETE CASCADE,
    FOREIGN KEY (option_set_id)         REFERENCES Car_Options(option_set_id) ON DELETE CASCADE,
    FOREIGN KEY (manufactured_plant_id) REFERENCES Manufacture_Plant(manufacture_plant_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Customers (
    customer_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name        TEXT NOT NULL,
    last_name         TEXT NOT NULL,
    gender            TEXT CHECK(gender IN ('Male', 'Female')),
    household_income  INTEGER,
    birthdate         DATE,
    phone_number      TEXT,
    email             TEXT UNIQUE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Dealer_Brand (
    dealer_brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dealer_id       INTEGER NOT NULL,
    brand_id        INTEGER NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dealer_id) REFERENCES Dealers(dealer_id) ON DELETE CASCADE,
    FOREIGN KEY (brand_id)  REFERENCES Brands(brand_id)   ON DELETE CASCADE,
    UNIQUE(dealer_id, brand_id)
);

CREATE TABLE IF NOT EXISTS Customer_Ownership (
    ownership_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id          INTEGER NOT NULL,
    vin                  INTEGER NOT NULL,
    purchase_date        DATE NOT NULL,
    purchase_price       DECIMAL(10, 2) NOT NULL CHECK(purchase_price > 0),
    warantee_expire_date DATE,
    dealer_id            INTEGER NOT NULL,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vin)         REFERENCES Car_Vins(vin)           ON DELETE CASCADE,
    FOREIGN KEY (dealer_id)   REFERENCES Dealers(dealer_id)      ON DELETE RESTRICT,
    UNIQUE(customer_id, vin)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_models_brand_id              ON Models(brand_id);
CREATE INDEX IF NOT EXISTS idx_car_parts_plant_id           ON Car_Parts(manufacture_plant_id);
CREATE INDEX IF NOT EXISTS idx_car_options_model_id         ON Car_Options(model_id);
CREATE INDEX IF NOT EXISTS idx_car_vins_model_id            ON Car_Vins(model_id);
CREATE INDEX IF NOT EXISTS idx_car_vins_plant_id            ON Car_Vins(manufactured_plant_id);
CREATE INDEX IF NOT EXISTS idx_customer_ownership_customer  ON Customer_Ownership(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_ownership_vin       ON Customer_Ownership(vin);
CREATE INDEX IF NOT EXISTS idx_customer_ownership_dealer    ON Customer_Ownership(dealer_id);
CREATE INDEX IF NOT EXISTS idx_dealer_brand_dealer          ON Dealer_Brand(dealer_id);
CREATE INDEX IF NOT EXISTS idx_dealer_brand_brand           ON Dealer_Brand(brand_id);
"""


def init_database(db_path: str = "database/sales.db") -> None:
    """
    Ensure the database exists with the correct automotive schema.
    Safe to call on an already-initialized DB (uses IF NOT EXISTS).
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        # Create automotive tables
        conn.executescript(_AUTOMOTIVE_SCHEMA_DDL)
        # Create qa_cache table (used by CacheAgent)
        conn.execute(_QA_CACHE_DDL)
        conn.commit()

    logger.info(f"✅ Automotive database schema verified at: {db_path}")


if __name__ == "__main__":
    init_database()
    logger.info("Database initialization complete.")

import sqlite3
from pathlib import Path
import logging
from faker import Faker
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database(db_path: str = "database/sales.db"):
    """Initialize SQLite database with e-commerce sales schema"""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL CHECK(price > 0),
            stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT,
            country TEXT,
            signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL CHECK(salary > 0),
            hire_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            employee_id INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL CHECK(total_amount >= 0),
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price > 0),
            subtotal REAL NOT NULL CHECK(subtotal > 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qa_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            normalized_question TEXT UNIQUE NOT NULL,
            original_question TEXT NOT NULL,
            sql_query TEXT NOT NULL,
            answer TEXT NOT NULL,
            evidence TEXT NOT NULL,
            confidence REAL NOT NULL,
            execution_time_ms REAL NOT NULL,
            token_usage TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    logger.info("Database schema created successfully")
    
    # Seed sample data
    seed_data(cursor)
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {db_path}")


def seed_data(cursor):
    """Seed database with sample e-commerce data"""
    fake = Faker()
    
    # Categories
    categories = [
        ("Electronics", "Electronic devices and gadgets"),
        ("Clothing", "Apparel and fashion items"),
        ("Home & Garden", "Home and garden products"),
        ("Sports", "Sports and outdoor equipment"),
        ("Books", "Books and educational materials")
    ]
    cursor.executemany(
        "INSERT INTO categories (name, description) VALUES (?, ?)",
        categories
    )
    logger.info("Seeded categories")
    
    # Products
    products = [
        (1, "Laptop", 999.99, 50, "High-performance laptop"),
        (1, "Smartphone", 699.99, 100, "Latest smartphone model"),
        (1, "Headphones", 199.99, 75, "Wireless headphones"),
        (2, "T-Shirt", 29.99, 200, "Cotton t-shirt"),
        (2, "Jeans", 79.99, 150, "Denim jeans"),
        (3, "Office Chair", 299.99, 40, "Ergonomic office chair"),
        (3, "Desk Lamp", 49.99, 80, "LED desk lamp"),
        (4, "Running Shoes", 129.99, 60, "Professional running shoes"),
        (4, "Yoga Mat", 39.99, 100, "Non-slip yoga mat"),
        (5, "Python Guide", 34.99, 30, "Complete Python programming guide")
    ]
    cursor.executemany(
        "INSERT INTO products (category_id, name, price, stock, description) VALUES (?, ?, ?, ?, ?)",
        products
    )
    logger.info("Seeded products")
    
    # Customers
    for _ in range(50):
        cursor.execute(
            "INSERT INTO customers (name, email, phone, city, country) VALUES (?, ?, ?, ?, ?)",
            (fake.name(), fake.email(), fake.phone_number(), fake.city(), fake.country())
        )
    logger.info("Seeded customers")
    
    # Employees
    departments = ["Sales", "Support", "Marketing", "Operations"]
    for _ in range(20):
        cursor.execute(
            "INSERT INTO employees (name, email, department, salary, hire_date) VALUES (?, ?, ?, ?, ?)",
            (fake.name(), fake.email(), random.choice(departments), random.uniform(30000, 120000), fake.date_between(start_date='-5y'))
        )
    logger.info("Seeded employees")
    
    # Orders and Order Items
    for customer_id in range(1, 51):
        for _ in range(random.randint(1, 5)):
            order_date = fake.date_time_between(start_date='-6m')
            cursor.execute(
                "INSERT INTO orders (customer_id, employee_id, order_date, status) VALUES (?, ?, ?, ?)",
                (customer_id, random.randint(1, 20), order_date, random.choice(["completed", "pending", "cancelled"]))
            )
            
            order_id = cursor.lastrowid
            total = 0
            
            for _ in range(random.randint(1, 4)):
                product_id = random.randint(1, 10)
                quantity = random.randint(1, 5)
                unit_price = [999.99, 699.99, 199.99, 29.99, 79.99, 299.99, 49.99, 129.99, 39.99, 34.99][product_id - 1]
                subtotal = quantity * unit_price
                total += subtotal
                
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (order_id, product_id, quantity, unit_price, subtotal)
                )
            
            cursor.execute(
                "UPDATE orders SET total_amount = ? WHERE id = ?",
                (total, order_id)
            )
    
    logger.info("Seeded orders and order items")


if __name__ == "__main__":
    init_database()
    logger.info("✅ Database initialization complete!")

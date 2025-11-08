"""
Database migration utilities.
"""
from sqlalchemy import text, inspect
from .database import engine


def migrate_add_expected_delivery_date():
    """Add expected_delivery_date column to orders table if it doesn't exist."""
    with engine.connect() as conn:
        # Check if column exists
        inspector = inspect(engine)
        columns = [col["name"] for col in inspector.get_columns("orders")]
        
        if "expected_delivery_date" not in columns:
            try:
                conn.execute(
                    text("ALTER TABLE orders ADD COLUMN expected_delivery_date DATETIME")
                )
                conn.commit()
                print("✓ Added expected_delivery_date column to orders table")
            except Exception as e:
                print(f"⚠ Migration error: {e}")
                conn.rollback()
        else:
            print("✓ expected_delivery_date column already exists")


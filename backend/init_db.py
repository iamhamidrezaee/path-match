"""
Database initialization script for PathMatch

Run this script to create the database tables:
    python init_db.py
"""

from app import app, db
import models

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Print table information
        print("\nCreated tables:")
        for table in db.metadata.sorted_tables:
            print(f"  - {table.name}")

if __name__ == '__main__':
    print("Initializing PathMatch database...")
    init_database()
    print("\nDatabase initialization complete!")


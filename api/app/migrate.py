#!/usr/bin/env python3
"""
Database migration script for creating tables
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import db
from models.User import User
from models.Segment import Segment

def create_tables():
    """Create all tables in the database"""
    
    try:
        if db.is_closed():
            db.connect()
        
        # Create tables
        db.create_tables([User, Segment], safe=True)
        
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
    finally:
        if not db.is_closed():
            db.close()

def create_tables_verbose():
    """Create all tables in the database with verbose output"""
    print("Connecting to database...")
    
    try:
        db.connect()
        print("Connected to database successfully")
        
        # Create tables
        print("Creating tables...")
        db.create_tables([User, Segment], safe=True)
        print("Tables created successfully!")
        
        # Verify tables were created
        tables = db.get_tables()
        print(f"Tables in database: {tables}")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()
            print("Database connection closed")
    
    return True

def drop_tables():
    """Drop all tables (use with caution!)"""
    print("Connecting to database...")
    
    try:
        db.connect()
        print("Connected to database successfully")
        
        # Drop tables
        print("Dropping tables...")
        db.drop_tables([User, Segment], safe=True)
        print("Tables dropped successfully!")
        
    except Exception as e:
        print(f"Error dropping tables: {e}")
        return False
    finally:
        if not db.is_closed():
            db.close()
            print("Database connection closed")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        print("WARNING: This will drop all tables!")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            drop_tables()
        else:
            print("Operation cancelled")
    else:
        create_tables_verbose()

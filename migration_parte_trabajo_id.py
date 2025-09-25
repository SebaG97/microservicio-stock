#!/usr/bin/env python3
"""
Migration script to add parte_trabajo_id column to stock_movimientos table
Run this script to update existing database schema
"""

import psycopg2
from database import SQLALCHEMY_DATABASE_URL

def migrate_database():
    """Add parte_trabajo_id column to stock_movimientos table"""
    
    print(f"Connecting to PostgreSQL database...")
    
    try:
        # Parse the SQLAlchemy URL to get connection parameters
        # Format: postgresql://user:password@host:port/database
        url_parts = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "").split("/")
        db_name = url_parts[1]
        auth_host = url_parts[0].split("@")
        auth = auth_host[0].split(":")
        host_port = auth_host[1].split(":")
        
        user = auth[0]
        password = auth[1]
        host = host_port[0] 
        port = host_port[1]
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'stock_movimientos' 
            AND column_name = 'parte_trabajo_id'
        """)
        
        if cursor.fetchone():
            print("Column 'parte_trabajo_id' already exists in stock_movimientos table")
            return True
        
        # Add the new column
        print("Adding parte_trabajo_id column to stock_movimientos table...")
        cursor.execute("""
            ALTER TABLE stock_movimientos 
            ADD COLUMN parte_trabajo_id INTEGER 
            REFERENCES partes_trabajo(id)
        """)
        
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'stock_movimientos' 
            AND column_name = 'parte_trabajo_id'
        """)
        
        if cursor.fetchone():
            print("✓ Column 'parte_trabajo_id' added successfully")
        else:
            print("✗ Error: Column was not added")
            return False
            
        return True
        
    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Stock Movement - Work Order Migration ===")
    print("This script will add the parte_trabajo_id column to link stock movements with work orders")
    
    success = migrate_database()
    
    if success:
        print("\n✓ Migration completed successfully!")
        print("You can now link stock movements to work orders using the parte_trabajo_id field")
    else:
        print("\n✗ Migration failed!")
        print("Please check the error messages above and try again")
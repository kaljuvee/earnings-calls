#!/usr/bin/env python3
"""
Run SQL initialization script
Creates views, functions, and triggers
"""

from dotenv import load_dotenv
load_dotenv()

import os
import psycopg2

def main():
    """Run SQL initialization"""
    
    print("=" * 70)
    print("RUNNING SQL INITIALIZATION SCRIPT")
    print("=" * 70)
    
    db_url = os.getenv('DB_URL')
    
    if not db_url:
        print("❌ Error: DB_URL not found")
        return False
    
    try:
        # Read SQL file
        print("\n📄 Reading SQL script...")
        with open('sql/init_postgres.sql', 'r') as f:
            sql_script = f.read()
        
        print(f"✅ SQL script loaded ({len(sql_script)} characters)")
        
        # Connect to database
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected")
        
        # Execute SQL script
        print("\n⚙️ Executing SQL script...")
        cursor.execute(sql_script)
        
        print("✅ SQL script executed successfully")
        
        # Verify views were created
        print("\n🔍 Verifying views...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'earnings'
        """)
        
        views = cursor.fetchall()
        
        if views:
            print(f"✅ Views created:")
            for view in views:
                print(f"   - {view[0]}")
        else:
            print("⚠️ No views found")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ SQL INITIALIZATION COMPLETE")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

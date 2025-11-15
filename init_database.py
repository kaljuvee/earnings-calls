#!/usr/bin/env python3
"""
Initialize PostgreSQL Database
Creates schema and tables for earnings call analyzer
"""

from dotenv import load_dotenv
load_dotenv()

import os
from utils.database import Database

def main():
    """Initialize database"""
    
    print("=" * 70)
    print("INITIALIZING POSTGRESQL DATABASE")
    print("=" * 70)
    
    # Get database URL
    db_url = os.getenv('DB_URL')
    
    if not db_url:
        print("❌ Error: DB_URL not found in environment variables")
        print("Please set DB_URL in .env file")
        return False
    
    print(f"\n📊 Database URL: {db_url.split('@')[1] if '@' in db_url else 'Not configured'}")
    
    try:
        # Initialize database
        print("\n🔧 Creating database connection...")
        db = Database(db_url)
        
        print("✅ Database connection established")
        print("✅ Schema 'earnings' created")
        print("✅ Tables created:")
        print("   - transcripts")
        print("   - analyses")
        print("   - price_movements")
        print("   - correlations")
        
        # Get database stats
        print("\n📊 Database Statistics:")
        stats = db.get_database_stats()
        
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "=" * 70)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

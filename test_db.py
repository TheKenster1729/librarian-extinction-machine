#!/usr/bin/env python3

from utils import DatabaseUtils

def test_database_connection():
    """Test the database connection functionality"""
    
    # Test with MySQL (default)
    print("Testing DatabaseUtils with MySQL database...")
    db_utils_mysql = DatabaseUtils(
        db_type="mysql",
        host="localhost",
        port=3306,
        username="root",
        password="",
        database="booklog"
    )
    print(f"Database dataframe shape: {db_utils_mysql.db_as_df.shape}")
    print(f"Database dataframe columns: {list(db_utils_mysql.db_as_df.columns)}")
    
    # Test the clean_database function
    if 'ReadingStatus' in db_utils_mysql.db_as_df.columns:
        print("\nTesting clean_database function...")
        print("Before cleaning - sample ReadingStatus entries:")
        sample_entries = db_utils_mysql.db_as_df['ReadingStatus'].dropna().head(5)
        for i, entry in enumerate(sample_entries):
            print(f"  {i+1}: '{entry}' (repr: {repr(entry)})")
        
        # Run the cleaning function
        success = db_utils_mysql.clean_database()
        print(f"Clean database result: {success}")
        
        if success:
            print("After cleaning - sample ReadingStatus entries:")
            sample_entries_after = db_utils_mysql.db_as_df['ReadingStatus'].dropna().head(5)
            for i, entry in enumerate(sample_entries_after):
                print(f"  {i+1}: '{entry}' (repr: {repr(entry)})")
    else:
        print("ReadingStatus column not found in the database.")
    
    print("-" * 50)
    
    # Test with PostgreSQL
    print("Testing DatabaseUtils with PostgreSQL database...")
    db_utils_postgres = DatabaseUtils(
        db_type="postgresql",
        host="localhost",
        port=5432,
        username="postgres",
        password="",
        database="booklog"
    )
    print(f"Database dataframe shape: {db_utils_postgres.db_as_df.shape}")
    print(f"Database dataframe columns: {list(db_utils_postgres.db_as_df.columns)}")

if __name__ == "__main__":
    test_database_connection() 
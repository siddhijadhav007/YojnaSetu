import pandas as pd
import sqlite3
import os
from datetime import datetime

def xlsx_to_sqlite(xlsx_file, db_file):
    """
    Convert XLSX file to SQLite database for viewing
    """
    print(f"Converting {xlsx_file} to SQLite database...")

    # Read the Excel file
    df = pd.read_excel(xlsx_file)

    # Create SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table
    table_name = 'schemes'

    # Get column names and types
    columns = []
    for col in df.columns:
        # Clean column names for SQL
        clean_col = col.replace(' ', '_').replace('-', '_').lower()
        columns.append(f'"{clean_col}" TEXT')

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {', '.join(columns)}
    )
    """

    cursor.execute(create_table_sql)

    # Insert data
    print(f"Inserting {len(df)} records...")

    for index, row in df.iterrows():
        # Prepare values
        values = []
        for col in df.columns:
            value = row[col]
            # Handle different data types
            if pd.isna(value):
                values.append(None)
            elif isinstance(value, (int, float)):
                values.append(str(value))
            else:
                values.append(str(value))

        # Create placeholders
        placeholders = ', '.join(['?' for _ in values])

        # Clean column names for SQL
        clean_columns = [col.replace(' ', '_').replace('-', '_').lower() for col in df.columns]
        columns_str = ', '.join([f'"{col}"' for col in clean_columns])

        insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        cursor.execute(insert_sql, values)

    # Create indexes for better query performance
    index_columns = ['category', 'scheme_provider_type', 'scheme_type', 'gender', 'occupation']
    for col in index_columns:
        if col in [c.replace(' ', '_').replace('-', '_').lower() for c in df.columns]:
            try:
                cursor.execute(f"CREATE INDEX idx_{col} ON {table_name}({col})")
            except:
                pass  # Index might already exist

    # Create a view for easy querying
    cursor.execute(f"""
    CREATE VIEW IF NOT EXISTS scheme_summary AS
    SELECT
        scheme_id,
        scheme_name,
        category,
        description,
        benefit_amount,
        min_age,
        max_age,
        gender,
        min_income,
        max_income,
        occupation,
        official_application_link
    FROM {table_name}
    """)

    conn.commit()
    conn.close()

    print(f"✅ Database created successfully: {db_file}")
    print(f"📊 Total records: {len(df)}")
    print(f"📋 Columns: {len(df.columns)}")

    return db_file

def view_database_info(db_file):
    """
    Display database information for verification
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n📋 Tables in database: {[t[0] for t in tables]}")

    # Get record count
    cursor.execute("SELECT COUNT(*) FROM schemes")
    count = cursor.fetchone()[0]
    print(f"📊 Total schemes: {count}")

    # Show sample data
    cursor.execute("SELECT scheme_name, category, benefit_amount FROM schemes LIMIT 5")
    rows = cursor.fetchall()
    print("\n📋 Sample data:")
    for row in rows:
        print(f"  - {row[0]} ({row[1]}) - {row[2]}")

    conn.close()

if __name__ == "__main__":
    xlsx_file = "yojna_setu_ai_cleaned.xlsx"
    db_file = "yojna_setu_ai_schemes.db"

    if os.path.exists(xlsx_file):
        # Convert XLSX to SQLite
        xlsx_to_sqlite(xlsx_file, db_file)

        # Show database info
        view_database_info(db_file)

        print(f"\n🎉 SQLite database ready for viewing: {db_file}")
        print("\n💡 You can now query the database using SQL commands:")
        print("   - SELECT * FROM schemes WHERE category = 'Education & Scholarships'")
        print("   - SELECT scheme_name, benefit_amount FROM scheme_summary LIMIT 10")
    else:
        print(f"❌ Error: {xlsx_file} not found!")
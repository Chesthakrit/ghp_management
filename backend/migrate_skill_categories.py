import psycopg2

DB_HOST = "localhost"
DB_NAME = "ghp_db"
DB_USER = "postgres"
DB_PASS = "1900"

print(f"Connecting to PostgreSQL database {DB_NAME}...")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Creating 'duty_categories' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS duty_categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        );
    """)
    
    print("Adding 'category_id' to 'duties' table...")
    try:
        cursor.execute("ALTER TABLE duties ADD COLUMN category_id INTEGER REFERENCES duty_categories(id);")
        print("Successfully added 'category_id' column.")
    except psycopg2.errors.DuplicateColumn:
        print("Column 'category_id' already exists.")
    
    print("Migration finished successfully.")
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print("Done.")

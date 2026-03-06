import psycopg2

# Database configuration - match your database.py format
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
    
    print("Executing ALTER TABLE command...")
    cursor.execute("ALTER TABLE job_titles ADD COLUMN level INTEGER DEFAULT 1;")
    
    print("Successfully added 'level' column to 'job_titles' table.")
    
except psycopg2.errors.DuplicateColumn as e:
    print("Column 'level' already exists. The database is already updated.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print("Done.")

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
    
    print("Executing ALTER TABLE command to add 'description' to 'duties' table...")
    cursor.execute("ALTER TABLE duties ADD COLUMN description VARCHAR;")
    
    print("Successfully added 'description' column to 'duties' table.")
    
except psycopg2.errors.DuplicateColumn as e:
    print("Column 'description' already exists. The database is already updated.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print("Done.")

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
    
    print("Creating 'user_duty_evaluations' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_duty_evaluations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            duty_id INTEGER NOT NULL REFERENCES duties(id) ON DELETE CASCADE,
            score INTEGER DEFAULT 0,
            evaluated_by_id INTEGER REFERENCES users(id),
            updated_at VARCHAR
        );
    """)
    
    print("Migration finished successfully.")
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print("Done.")

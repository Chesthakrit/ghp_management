"""
Migration: add nickname, photo_path, id_doc_path columns (PostgreSQL)
Run ONCE: python migrate_register_v2.py
"""
from database import engine
from sqlalchemy import text

def column_exists(conn, table, column):
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = :table AND column_name = :col
    """), {"table": table, "col": column}).fetchone()
    return result is not None

def run():
    with engine.connect() as conn:
        if not column_exists(conn, "users", "nickname"):
            print("Adding nickname column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR"))
        else:
            print("nickname already exists, skipping.")

        if not column_exists(conn, "users", "photo_path"):
            print("Adding photo_path column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN photo_path VARCHAR"))
        else:
            print("photo_path already exists, skipping.")

        if not column_exists(conn, "users", "id_doc_path"):
            print("Adding id_doc_path column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN id_doc_path VARCHAR"))
        else:
            print("id_doc_path already exists, skipping.")

        conn.commit()
        print("\nMigration complete!")

if __name__ == "__main__":
    run()

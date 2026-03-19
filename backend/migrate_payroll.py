from sqlalchemy import text
from database import engine

def migrate():
    print("🚀 Starting Payroll Migration (Fix)...")
    
    with engine.begin() as conn: # Use begin() for auto-commit
        # 1. Update employee_profiles
        try:
            print("Checking/Adding 'base_salary'...")
            conn.execute(text("ALTER TABLE employee_profiles ADD COLUMN IF NOT EXISTS base_salary INTEGER DEFAULT 0"))
            
            print("Checking/Adding 'bank_account'...")
            conn.execute(text("ALTER TABLE employee_profiles ADD COLUMN IF NOT EXISTS bank_account VARCHAR"))
            print("✅ employee_profiles columns ensured.")
        except Exception as e:
            print(f"⚠️ Warning (employee_profiles): {e}")

        # 2. Create payroll_settings
        try:
            print("Ensuring 'payroll_settings' table exists...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payroll_settings (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR UNIQUE,
                    value FLOAT,
                    description VARCHAR,
                    type VARCHAR DEFAULT 'float'
                )
            """))
            print("✅ payroll_settings table is ready.")
        except Exception as e:
            print(f"⚠️ Warning (payroll_settings): {e}")

    print("🎉 Migration Completed Successfully!")

if __name__ == "__main__":
    migrate()

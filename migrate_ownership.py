import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def run():
    print("Connecting to database...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'password'),
            database=os.getenv('DB_NAME', 'job_tracker'),
            ssl_ca=os.getenv('SSL_CA_CERT'),
            ssl_disabled=False
        )
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    cursor = conn.cursor()

    alterations = [
        ("companies",    "created_by", "ALTER TABLE companies ADD COLUMN created_by INT NULL"),
        ("jobs",         "created_by", "ALTER TABLE jobs ADD COLUMN created_by INT NULL"),
        ("contacts",     "created_by", "ALTER TABLE contacts ADD COLUMN created_by INT NULL"),
        ("applications", "user_id",    "ALTER TABLE applications ADD COLUMN user_id INT NULL"),
    ]

    for table, col, sql in alterations:
        print(f"Adding {col} to {table}...")
        try:
            cursor.execute(sql)
            print(f"  Done.")
        except mysql.connector.Error as e:
            if e.errno == 1060:
                print(f"  Already exists — skipping.")
            else:
                print(f"  Error: {e}")

    # Add FKs (ignore if already exist)
    fk_statements = [
        "ALTER TABLE companies ADD CONSTRAINT fk_co_user FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL",
        "ALTER TABLE jobs ADD CONSTRAINT fk_job_user FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL",
        "ALTER TABLE contacts ADD CONSTRAINT fk_ct_user FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL",
        "ALTER TABLE applications ADD CONSTRAINT fk_app_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL",
    ]
    for fk in fk_statements:
        try:
            cursor.execute(fk)
        except mysql.connector.Error as e:
            pass  # Already exists

    print("Assigning all unowned records to admin (id=1)...")
    assignments = [
        "UPDATE companies SET created_by = 1 WHERE created_by IS NULL",
        "UPDATE jobs SET created_by = 1 WHERE created_by IS NULL",
        "UPDATE contacts SET created_by = 1 WHERE created_by IS NULL",
        "UPDATE applications SET user_id = 1 WHERE user_id IS NULL",
    ]
    for sql in assignments:
        cursor.execute(sql)
        print(f"  {cursor.rowcount} rows updated: {sql[:40]}...")

    conn.commit()
    print("\nMigration complete!")
    conn.close()

if __name__ == '__main__':
    run()

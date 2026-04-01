import ssl
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def run_seed():
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
    
    print("Altering applications table to expand status ENUM...")
    try:
        # We include old ENUMs ('Screening') to not break existing data, and append the new detailed ones.
        enum_definition = "'Applied', 'Screening', 'Phone Screen', 'Interview Scheduled', 'Interview', 'Interview Completed', 'Offer', 'Offer Accepted', 'Rejected', 'Withdrawn'"
        cursor.execute(f"ALTER TABLE applications MODIFY COLUMN status ENUM({enum_definition})")
        conn.commit()
        print("Status column logic successfully altered!")
    except mysql.connector.Error as err:
        print(f"Error altering table: {err}")
        
    conn.close()

if __name__ == '__main__':
    run_seed()

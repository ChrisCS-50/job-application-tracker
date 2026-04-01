import ssl
import json
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
        
    cursor = conn.cursor(dictionary=True)
    
    print("Altering applications table to include interview_notes...")
    try:
        cursor.execute("ALTER TABLE applications ADD COLUMN interview_notes TEXT")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("interview_notes column already exists.")
        else:
            print(f"Error altering table: {err}")
            
    print("Backfilling interview notes for existing Interview applications...")
    cursor.execute("UPDATE applications SET interview_notes = 'Met with Hiring Manager. Expected architectural system design questions up next. Focus heavily on SQL joins.' WHERE status = 'Interview' AND (interview_notes IS NULL OR interview_notes = '')")
    
    print("Checking for orphaned companies (without jobs)...")
    cursor.execute('''
        SELECT c.company_id, c.company_name FROM companies c 
        LEFT JOIN jobs j ON c.company_id = j.company_id 
        WHERE j.job_id IS NULL
    ''')
    orphaned_jobs = cursor.fetchall()
    for company in orphaned_jobs:
        print(f"Adding generic job for {company['company_name']}...")
        cursor.execute('''
            INSERT INTO jobs (company_id, job_title, job_url, requirements) 
            VALUES (%s, %s, %s, %s)
        ''', (company['company_id'], 'Software Engineer', 'https://example.com/careers', '[{"skill": "Python"}, {"skill": "SQL"}]'))
        
    print("Checking for orphaned companies (without contacts)...")
    cursor.execute('''
        SELECT c.company_id, c.company_name FROM companies c 
        LEFT JOIN contacts con ON c.company_id = con.company_id 
        WHERE con.contact_id IS NULL
    ''')
    orphaned_contacts = cursor.fetchall()
    for company in orphaned_contacts:
        print(f"Adding generic HR contact for {company['company_name']}...")
        cursor.execute('''
            INSERT INTO contacts (company_id, contact_name, title, notes) 
            VALUES (%s, %s, %s, %s)
        ''', (company['company_id'], 'Jane Doe', 'HR Representative', 'Met at virtual networking event.'))
        
    conn.commit()
    print("Seed Part 2 logic completed!")
    conn.close()

if __name__ == '__main__':
    run_seed()

import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load env variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_DATABASE = os.getenv('DB_DATABASE', 'job_tracker')
DB_PORT = os.getenv('DB_PORT', '3306')

def seed_db():
    print("Connecting to database...")
    conn = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE, port=DB_PORT
    )
    cursor = conn.cursor()
    
    print("Migrating users table...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        is_admin BOOLEAN DEFAULT TRUE
    )
    ''')
    
    print("Migrating applications table...")
    try:
        cursor.execute('ALTER TABLE applications ADD COLUMN cover_letter_text TEXT;')
        print("Added cover_letter_text.")
    except Exception as e:
        if "Duplicate column name" not in str(e):
            print(f"Error adding cover_letter_text: {e}")
            
    try:
        cursor.execute('ALTER TABLE applications ADD COLUMN resume_file_path VARCHAR(255);')
        print("Added resume_file_path.")
    except Exception as e:
        if "Duplicate column name" not in str(e):
            print(f"Error adding resume_file_path: {e}")
            
    print("Creating admin user...")
    cursor.execute("SELECT id FROM users WHERE username='admin'")
    admin = cursor.fetchone()
    if not admin:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", 
                       ('admin', generate_password_hash('password123')))
    
    # insert advanced mock data (to test tooltips)
    print("Seeding mock testing data (keeping your existing data safe)...")
    cursor.execute("SELECT company_id FROM companies WHERE company_name='Stark Industries'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO companies (company_name, industry, website, city, state, notes) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', ("Stark Industries", "Technology", "https://stark.com", "New York", "NY", "Hover Note: Global leader in enterprise tech and defense AI. Looking for Flask specialists."))
        company_id = cursor.lastrowid
        
        cursor.execute('''
        INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, date_posted, requirements)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (company_id, "Senior AI Engineer", "Full-time", 150000, 250000, "2026-03-28", '["Python", "Flask", "MySQL", "GenAI"]'))
        job_id = cursor.lastrowid
        
        cursor.execute('''
        INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, cover_letter_text, resume_file_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (job_id, "2026-03-28", "Interview", "AI_Specialist_v2.pdf", True, 
              "Dear Hiring Manager,\n\nI am thrilled to apply for the Senior AI Engineer role at Stark Industries. With my extensive background building Python/Flask applications tied to robust MySQL architectures, I am confident I can immediately contribute to your GenAI implementations.\n\nThank you for considering my application.\n\nBest,\nAdmin Candidate",
              "/static/uploads/dummy_resume.pdf"))
              
        cursor.execute('''
        INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (company_id, "Tony Stark", "CEO", "tony@stark.com", "555-0199", "https://linkedin.com/in/stark", "Hover Note: Very interested in backend GenAI skill match features."))
        
        print("Seed data injected successfully!")
    else:
        print("Seed data already exists.")
        
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    seed_db()

import os
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

class JobTrackerDB:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'database': os.getenv('DB_DATABASE', 'job_tracker'),
            'port': os.getenv('DB_PORT', '3306')
        }
    
    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f'Database connection error: {e}')
            return None

    # --- COMPANIES ---
    def get_all_companies(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM companies ORDER BY company_name')
            return cursor.fetchall()
        finally:
            conn.close()
            
    def get_company(self, company_id):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM companies WHERE company_id = %s', (company_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def add_company(self, name, industry, website, city, state, notes):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = '''INSERT INTO companies (company_name, industry, website, city, state, notes)
                       VALUES (%s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (name, industry, website, city, state, notes))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding company: {e}")
            return False
        finally:
            conn.close()

    def update_company(self, company_id, name, industry, website, city, state, notes):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = '''UPDATE companies 
                       SET company_name=%s, industry=%s, website=%s, city=%s, state=%s, notes=%s
                       WHERE company_id=%s'''
            cursor.execute(query, (name, industry, website, city, state, notes, company_id))
            conn.commit()
            return True
        except Error as e:
            print(f"Error updating company: {e}")
            return False
        finally:
            conn.close()

    def delete_company(self, company_id):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM companies WHERE company_id = %s', (company_id,))
            conn.commit()
            return True
        except Error as e:
            print(f"Error deleting company: {e}")
            return False
        finally:
            conn.close()

    # --- JOBS ---
    def get_all_jobs(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = '''SELECT j.*, c.company_name 
                       FROM jobs j 
                       LEFT JOIN companies c ON j.company_id = c.company_id 
                       ORDER BY j.date_posted DESC'''
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def get_job(self, job_id):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            query = '''SELECT j.*, c.company_name 
                       FROM jobs j 
                       LEFT JOIN companies c ON j.company_id = c.company_id 
                       WHERE j.job_id = %s'''
            cursor.execute(query, (job_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def add_job(self, company_id, title, job_type, salary_min, salary_max, url, date_posted, requirements):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # requirements should be a json string
            req_json = json.dumps(requirements) if isinstance(requirements, list) else requirements
            query = '''INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (company_id, title, job_type, salary_min, salary_max, url, date_posted, req_json))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding job: {e}")
            return False
        finally:
            conn.close()

    def update_job(self, job_id, company_id, title, job_type, salary_min, salary_max, url, date_posted, requirements):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            req_json = json.dumps(requirements) if isinstance(requirements, list) else requirements
            query = '''UPDATE jobs 
                       SET company_id=%s, job_title=%s, job_type=%s, salary_min=%s, salary_max=%s, job_url=%s, date_posted=%s, requirements=%s
                       WHERE job_id=%s'''
            cursor.execute(query, (company_id, title, job_type, salary_min, salary_max, url, date_posted, req_json, job_id))
            conn.commit()
            return True
        except Error as e:
            print(f"Error updating job: {e}")
            return False
        finally:
            conn.close()

    def delete_job(self, job_id):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM jobs WHERE job_id = %s', (job_id,))
            conn.commit()
            return True
        except Error as e:
            return False
        finally:
            conn.close()

    # --- APPLICATIONS ---
    def get_all_applications(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = '''SELECT a.*, j.job_title, c.company_name 
                       FROM applications a 
                       JOIN jobs j ON a.job_id = j.job_id
                       JOIN companies c ON j.company_id = c.company_id
                       ORDER BY a.application_date DESC'''
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def get_application(self, application_id):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            query = '''SELECT a.*, j.job_title, c.company_name 
                       FROM applications a 
                       JOIN jobs j ON a.job_id = j.job_id
                       JOIN companies c ON j.company_id = c.company_id
                       WHERE application_id = %s'''
            cursor.execute(query, (application_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def add_application(self, job_id, app_date, status, resume_ver, cl_sent, interview_data):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            int_json = json.dumps(interview_data) if interview_data else None
            query = '''INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
                       VALUES (%s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (job_id, app_date, status, resume_ver, cl_sent, int_json))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding app: {e}")
            return False
        finally:
            conn.close()

    def update_application(self, application_id, job_id, app_date, status, resume_ver, cl_sent, interview_data):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            int_json = json.dumps(interview_data) if interview_data else None
            query = '''UPDATE applications 
                       SET job_id=%s, application_date=%s, status=%s, resume_version=%s, cover_letter_sent=%s, interview_data=%s
                       WHERE application_id=%s'''
            cursor.execute(query, (job_id, app_date, status, resume_ver, cl_sent, int_json, application_id))
            conn.commit()
            return True
        except Error as e:
            print(f"Error updating app: {e}")
            return False
        finally:
            conn.close()

    def delete_application(self, application_id):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM applications WHERE application_id = %s', (application_id,))
            conn.commit()
            return True
        except Error as e:
            return False
        finally:
            conn.close()

    # --- CONTACTS ---
    def get_all_contacts(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = '''SELECT ct.*, c.company_name 
                       FROM contacts ct 
                       LEFT JOIN companies c ON ct.company_id = c.company_id
                       ORDER BY ct.contact_name'''
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def get_contact(self, contact_id):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            query = '''SELECT ct.*, c.company_name 
                       FROM contacts ct 
                       LEFT JOIN companies c ON ct.company_id = c.company_id
                       WHERE contact_id = %s'''
            cursor.execute(query, (contact_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def add_contact(self, company_id, name, title, email, phone, linkedin, notes):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = '''INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (company_id, name, title, email, phone, linkedin, notes))
            conn.commit()
            return True
        except Error as e:
            return False
        finally:
            conn.close()

    def update_contact(self, contact_id, company_id, name, title, email, phone, linkedin, notes):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = '''UPDATE contacts 
                       SET company_id=%s, contact_name=%s, title=%s, email=%s, phone=%s, linkedin_url=%s, notes=%s
                       WHERE contact_id=%s'''
            cursor.execute(query, (company_id, name, title, email, phone, linkedin, notes, contact_id))
            conn.commit()
            return True
        except Error as e:
            return False
        finally:
            conn.close()

    def delete_contact(self, contact_id):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM contacts WHERE contact_id = %s', (contact_id,))
            conn.commit()
            return True
        except Error as e:
            return False
        finally:
            conn.close()

    # --- DASHBOARD STATS ---
    def get_dashboard_stats(self):
        conn = self.get_connection()
        stats = {
            'total_applications': 0,
            'interviews': 0,
            'offers': 0,
            'rejections': 0,
            'active_applications': 0,
            'recent_applications': []
        }
        if not conn: return stats
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as count FROM applications")
            stats['total_applications'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM applications WHERE status = 'Interview'")
            stats['interviews'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM applications WHERE status = 'Offer'")
            stats['offers'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM applications WHERE status = 'Rejected'")
            stats['rejections'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM applications WHERE status IN ('Applied', 'Screening', 'Interview')")
            stats['active_applications'] = cursor.fetchone()['count']

            query = '''SELECT a.application_date, a.status, j.job_title, c.company_name 
                       FROM applications a 
                       JOIN jobs j ON a.job_id = j.job_id
                       JOIN companies c ON j.company_id = c.company_id
                       ORDER BY a.application_date DESC LIMIT 5'''
            cursor.execute(query)
            stats['recent_applications'] = cursor.fetchall()
            return stats
        finally:
            conn.close()

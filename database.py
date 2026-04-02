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

    # --- USERS / AUTH ---
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_user_by_username(self, username):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_all_users(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT id, username, is_admin FROM users ORDER BY id ASC')
            return cursor.fetchall()
        finally:
            conn.close()

    def create_user(self, username, password_hash, is_admin=False):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)', (username, password_hash, bool(is_admin)))
            conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()

    def update_user_role(self, user_id, is_admin):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_admin = %s WHERE id = %s', (bool(is_admin), user_id))
            conn.commit()
            return True
        except mysql.connector.Error as e:
            return False
        finally:
            conn.close()

    # --- COMPANIES ---
    def get_all_companies(self, user_id=None):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            if user_id is None:
                query = '''SELECT c.*, u.username as owner_username
                           FROM companies c
                           LEFT JOIN users u ON c.created_by = u.id
                           ORDER BY c.company_name'''
                cursor.execute(query)
            else:
                query = '''SELECT c.*, u.username as owner_username
                           FROM companies c
                           LEFT JOIN users u ON c.created_by = u.id
                           WHERE c.created_by = %s
                           ORDER BY c.company_name'''
                cursor.execute(query, (user_id,))
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

    def get_company_profile(self, company_id):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            # Get basic company data
            cursor.execute('SELECT * FROM companies WHERE company_id = %s', (company_id,))
            company = cursor.fetchone()
            if not company: return None
            
            # Get associated jobs
            cursor.execute('SELECT * FROM jobs WHERE company_id = %s ORDER BY date_posted DESC', (company_id,))
            jobs = cursor.fetchall()
            
            # Get associated contacts
            cursor.execute('SELECT * FROM contacts WHERE company_id = %s', (company_id,))
            contacts = cursor.fetchall()
            
            return {'company': company, 'jobs': jobs, 'contacts': contacts}
        finally:
            conn.close()

    def add_company(self, name, industry, website, city, state, notes, created_by=None):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = '''INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (name, industry, website, city, state, notes, created_by))
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
            # Find associated jobs to delete their applications
            cursor.execute('SELECT job_id FROM jobs WHERE company_id = %s', (company_id,))
            jobs = cursor.fetchall()
            for job in jobs:
                cursor.execute('DELETE FROM applications WHERE job_id = %s', (job[0],))
            
            # Delete associated jobs and contacts
            cursor.execute('DELETE FROM jobs WHERE company_id = %s', (company_id,))
            cursor.execute('DELETE FROM contacts WHERE company_id = %s', (company_id,))
            
            # Finally, delete the company
            cursor.execute('DELETE FROM companies WHERE company_id = %s', (company_id,))
            conn.commit()
            return True
        except Error as e:
            print(f"Error deleting company: {e}")
            return False
        finally:
            conn.close()

    # --- JOBS ---
    def get_all_jobs(self, user_id=None):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            if user_id is None:
                query = '''SELECT j.*, c.company_name, u.username as owner_username
                           FROM jobs j
                           LEFT JOIN companies c ON j.company_id = c.company_id
                           LEFT JOIN users u ON j.created_by = u.id
                           ORDER BY j.date_posted DESC'''
                cursor.execute(query)
            else:
                query = '''SELECT j.*, c.company_name, u.username as owner_username
                           FROM jobs j
                           LEFT JOIN companies c ON j.company_id = c.company_id
                           LEFT JOIN users u ON j.created_by = u.id
                           WHERE j.created_by = %s
                           ORDER BY j.date_posted DESC'''
                cursor.execute(query, (user_id,))
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

    def add_job(self, company_id, title, job_type, salary_min, salary_max, url, date_posted, requirements, created_by=None):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            req_json = json.dumps(requirements) if isinstance(requirements, list) else requirements
            query = '''INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements, created_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (company_id, title, job_type, salary_min, salary_max, url, date_posted, req_json, created_by))
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
            # Delete associated applications first
            cursor.execute('DELETE FROM applications WHERE job_id = %s', (job_id,))
            # Delete the job
            cursor.execute('DELETE FROM jobs WHERE job_id = %s', (job_id,))
            conn.commit()
            return True
        except Error as e:
            print(f"Error deleting job: {e}")
            return False
        finally:
            conn.close()

    # --- APPLICATIONS ---
    def get_all_applications(self, user_id=None):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            if user_id is None:
                query = '''SELECT a.*, j.job_title, c.company_name, c.company_id,
                                  u.username as owner_username
                           FROM applications a
                           JOIN jobs j ON a.job_id = j.job_id
                           JOIN companies c ON j.company_id = c.company_id
                           LEFT JOIN users u ON a.user_id = u.id
                           ORDER BY a.application_date DESC'''
                cursor.execute(query)
            else:
                query = '''SELECT a.*, j.job_title, c.company_name, c.company_id,
                                  u.username as owner_username
                           FROM applications a
                           JOIN jobs j ON a.job_id = j.job_id
                           JOIN companies c ON j.company_id = c.company_id
                           LEFT JOIN users u ON a.user_id = u.id
                           WHERE a.user_id = %s
                           ORDER BY a.application_date DESC'''
                cursor.execute(query, (user_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_application(self, application_id):
        conn = self.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            query = '''SELECT a.*, j.job_title, c.company_name, c.company_id 
                       FROM applications a 
                       JOIN jobs j ON a.job_id = j.job_id
                       JOIN companies c ON j.company_id = c.company_id
                       WHERE application_id = %s'''
            cursor.execute(query, (application_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def add_application(self, job_id, app_date, status, resume_ver, cl_sent, interview_data, user_id=None, interview_contacts=None):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            int_json = json.dumps(interview_data) if interview_data else None
            query = '''INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data, user_id, interview_contacts)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (job_id, app_date, status, resume_ver, cl_sent, int_json, user_id, interview_contacts))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding app: {e}")
            return False
        finally:
            conn.close()

    def update_application(self, application_id, job_id, app_date, status, resume_ver, cl_sent, interview_data, interview_contacts=None):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            int_json = json.dumps(interview_data) if interview_data else None
            query = '''UPDATE applications 
                       SET job_id=%s, application_date=%s, status=%s, resume_version=%s, cover_letter_sent=%s, interview_data=%s, interview_contacts=%s
                       WHERE application_id=%s'''
            cursor.execute(query, (job_id, app_date, status, resume_ver, cl_sent, int_json, interview_contacts, application_id))
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
            print(f"Error in delete_application: {e}")
            return False
        finally:
            conn.close()

    # --- CONTACTS ---
    def get_all_contacts(self, user_id=None):
        conn = self.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            if user_id is None:
                query = '''SELECT ct.*, c.company_name, u.username as owner_username
                           FROM contacts ct
                           LEFT JOIN companies c ON ct.company_id = c.company_id
                           LEFT JOIN users u ON ct.created_by = u.id
                           ORDER BY ct.contact_name'''
                cursor.execute(query)
            else:
                query = '''SELECT ct.*, c.company_name, u.username as owner_username
                           FROM contacts ct
                           LEFT JOIN companies c ON ct.company_id = c.company_id
                           LEFT JOIN users u ON ct.created_by = u.id
                           WHERE ct.created_by = %s
                           ORDER BY ct.contact_name'''
                cursor.execute(query, (user_id,))
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

    def add_contact(self, company_id, name, title, email, phone, linkedin, notes, created_by=None):
        conn = self.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = '''INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes, created_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(query, (company_id, name, title, email, phone, linkedin, notes, created_by))
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
    def get_dashboard_stats(self, user_id=None, is_admin=False, view_scope='personal'):
        """Compute dashboard stats based on view scope."""
        conn = self.get_connection()
        stats = {
            'total_applications': 0, 'total_all_applications': 0,
            'applied': 0, 'screening': 0, 'phone_screen': 0,
            'interview_scheduled': 0, 'interviews': 0, 'interview_completed': 0,
            'offers': 0, 'offer_accepted': 0, 'rejections': 0, 'withdrawn': 0,
            'active_applications': 0, 'recent_applications': [],
            'total_users': 0, 'total_companies': 0, 'total_jobs': 0,
            'is_admin_view': is_admin
        }
        if not conn: return stats
        try:
            cursor = conn.cursor(dictionary=True)
            uid = int(user_id) if user_id else 0

            if is_admin and view_scope == 'all':
                cursor.execute("SELECT COUNT(*) as count FROM applications")
                stats['total_applications'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM users")
                stats['total_users'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM companies")
                stats['total_companies'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM jobs")
                stats['total_jobs'] = cursor.fetchone()['count']

                status_where = ''
                active_where = "WHERE a.status IN"
                recent_where = ''
            else:
                cursor.execute("SELECT COUNT(*) as count FROM applications a WHERE a.user_id = %s", (uid,))
                stats['total_applications'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM companies WHERE created_by = %s", (uid,))
                stats['total_companies'] = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM jobs WHERE created_by = %s", (uid,))
                stats['total_jobs'] = cursor.fetchone()['count']

                status_where = f'WHERE a.user_id = {uid}'
                active_where = f"WHERE a.user_id = {uid} AND a.status IN"
                recent_where = f'WHERE a.user_id = {uid}'

            # Status breakdown for funnel chart
            cursor.execute(f"SELECT status, COUNT(*) as count FROM applications a {status_where} GROUP BY status")
            rows = cursor.fetchall()
            for r in rows:
                s = r['status']
                if s == 'Applied':               stats['applied'] = r['count']
                elif s == 'Screening':           stats['screening'] = r['count']
                elif s == 'Phone Screen':        stats['phone_screen'] = r['count']
                elif s == 'Interview Scheduled': stats['interview_scheduled'] = r['count']
                elif s == 'Interview':           stats['interviews'] = r['count']
                elif s == 'Interview Completed': stats['interview_completed'] = r['count']
                elif s == 'Offer':               stats['offers'] = r['count']
                elif s == 'Offer Accepted':      stats['offer_accepted'] = r['count']
                elif s == 'Rejected':            stats['rejections'] = r['count']
                elif s == 'Withdrawn':           stats['withdrawn'] = r['count']

            # Active applications count
            active_statuses = "('Applied','Screening','Phone Screen','Interview Scheduled','Interview','Interview Completed')"
            cursor.execute(f"SELECT COUNT(*) as count FROM applications a {active_where} {active_statuses}")
            stats['active_applications'] = cursor.fetchone()['count']

            # Recent activity
            query = f'''SELECT a.application_date, a.status, j.job_title, c.company_name, c.company_id
                       FROM applications a
                       JOIN jobs j ON a.job_id = j.job_id
                       JOIN companies c ON j.company_id = c.company_id
                       {recent_where}
                       ORDER BY a.application_date DESC LIMIT 5'''
            cursor.execute(query)
            stats['recent_applications'] = cursor.fetchall()
            # Salary Bins for Applications
            salary_query = f'''
                SELECT j.salary_min
                FROM applications a
                JOIN jobs j ON a.job_id = j.job_id
                {status_where}
            '''
            cursor.execute(salary_query)
            salary_rows = cursor.fetchall()
            salary_bins = {"< $50k": 0, "$50k - $80k": 0, "$80k - $120k": 0, "$120k - $150k": 0, "$150k+": 0}
            for row in salary_rows:
                s = row['salary_min']
                if not s: continue
                if s < 50000: salary_bins["< $50k"] += 1
                elif s <= 80000: salary_bins["$50k - $80k"] += 1
                elif s <= 120000: salary_bins["$80k - $120k"] += 1
                elif s <= 150000: salary_bins["$120k - $150k"] += 1
                else: salary_bins["$150k+"] += 1
            stats['salary_bins'] = salary_bins

            return stats
        finally:
            conn.close()

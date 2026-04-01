"""
Seed realistic companies, jobs, contacts, and applications for non-admin users.
User IDs 2 and 3 each get ~8 applications with proper ownership chains.
"""
import mysql.connector
import os
import json
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_DATABASE'),
    ssl_ca=os.getenv('SSL_CA_CERT'),
)
cur = conn.cursor(dictionary=True)

# ── Discover non-admin users ────────────────────────────────────────────────
cur.execute("SELECT id, username FROM users WHERE is_admin = 0 ORDER BY id")
non_admins = cur.fetchall()
print(f"Non-admin users: {non_admins}")
if not non_admins:
    print("No non-admin users found — nothing to seed.")
    conn.close()
    exit()

def insert(sql, params):
    cur.execute(sql, params)
    return cur.lastrowid

# ════════════════════════════════════════════════════════════════════════════
# USER A: First non-admin — Marcus Webb, recent CS grad job hunting
# ════════════════════════════════════════════════════════════════════════════
uid_a = non_admins[0]['id']
uname_a = non_admins[0]['username']
print(f"\nSeeding data for user A: {uname_a} (id={uid_a})")

# Companies owned by user A
co_a1 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
    ('Nexora Systems', 'Software Development', 'https://nexora.io', 'Atlanta', 'GA',
     'Mid-size SaaS company. Strong engineering culture. Remote-friendly.', uid_a))

co_a2 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
    ('PulseData Inc', 'Data Analytics', 'https://pulsedata.co', 'Austin', 'TX',
     'Fast-growing startup. Raised Series B in 2024.', uid_a))

co_a3 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
    ('Meridian Health Tech', 'Healthcare Technology', 'https://meridianht.com', 'Nashville', 'TN',
     'Health data platform. Good work-life balance per Glassdoor.', uid_a))

co_a4 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
    VALUES (%s,%s,%s,%s,%s,%s,%s)""",
    ('ClearPath Logistics', 'Logistics & Supply Chain', 'https://clearpathlog.com', 'Dallas', 'TX',
     'Logistics SaaS. Expanding engineering team Q2 2025.', uid_a))

# Jobs owned by user A
job_a1 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
    job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a1, 'Junior Software Engineer', 'Full-time', 75000, 95000,
     'https://nexora.io/careers/jse', '2025-03-01',
     json.dumps(['Python', 'REST APIs', 'Git', 'SQL', '2+ years experience']), uid_a))

job_a2 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
    job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a1, 'Backend Engineer', 'Full-time', 90000, 115000,
     'https://nexora.io/careers/be', '2025-02-20',
     json.dumps(['Python or Go', 'PostgreSQL', 'Docker', 'Microservices']), uid_a))

job_a3 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
    job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a2, 'Data Engineer', 'Full-time', 85000, 110000,
     'https://pulsedata.co/jobs/de', '2025-03-05',
     json.dumps(['Apache Spark', 'Python', 'Airflow', 'AWS', 'ETL pipelines']), uid_a))

job_a4 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
    job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a2, 'Analytics Engineer', 'Full-time', 80000, 100000,
     'https://pulsedata.co/jobs/ae', '2025-02-28',
     json.dumps(['dbt', 'SQL', 'Python', 'Looker or Tableau']), uid_a))

job_a5 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
    job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a3, 'Software Developer', 'Full-time', 80000, 100000,
     'https://meridianht.com/careers/sd', '2025-01-25',
     json.dumps(['Java or Python', 'REST APIs', 'HIPAA knowledge preferred', 'PostgreSQL']), uid_a))

job_a6 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
    job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a4, 'Full Stack Developer', 'Full-time', 88000, 108000,
     'https://clearpathlog.com/jobs/fsd', '2025-02-10',
     json.dumps(['React', 'Node.js', 'PostgreSQL', 'Docker', 'TypeScript']), uid_a))

# Contacts owned by user A
insert("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
    linkedin_url, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a1, 'Jordan Mills', 'Senior Recruiter', 'j.mills@nexora.io', '555-0101',
     'https://linkedin.com/in/jordanmills-recruiter',
     'Very responsive. Prefers communication over email. Reached out via LinkedIn first.', uid_a))

insert("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
    linkedin_url, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a1, 'Priya Sharma', 'Engineering Manager', 'p.sharma@nexora.io', '555-0102',
     'https://linkedin.com/in/priyasharma-eng',
     'Interviewed with her for the Backend role. Great technical depth. Harvard grad.', uid_a))

insert("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
    linkedin_url, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a2, 'Derek Okafor', 'Talent Acquisition', 'd.okafor@pulsedata.co', '555-0103',
     'https://linkedin.com/in/derekokafor',
     'Met at Atlanta Tech Week. He mentioned openings for data engineering roles.', uid_a))

insert("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
    linkedin_url, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
    (co_a3, 'Sandra Lee', 'HR Manager', 's.lee@meridianht.com', '555-0104',
     None, 'Sent initial application through company portal. Awaiting response.', uid_a))

# Applications owned by user A
apps_a = [
    # (job_id, date, status, resume_ver, cl_sent, notes)
    (job_a1, '2025-03-03', 'Interview Completed', 'v2.1', 1,
     'Had two interview rounds. Waiting for final decision. Went very well — discussed system design.'),
    (job_a2, '2025-02-22', 'Rejected', 'v2.0', 1,
     'Rejection email received after technical screening. Feedback: required more Go experience.'),
    (job_a3, '2025-03-07', 'Interview Scheduled', 'v2.1', 1,
     'Phone screen passed. Panel interview scheduled for March 18th with data team.'),
    (job_a4, '2025-03-01', 'Screening', 'v2.1', 1,
     'Resume reviewed. Recruiter Derek reached out to schedule initial phone screen.'),
    (job_a5, '2025-01-28', 'Offer', 'v1.9', 1,
     'Verbal offer made: $92,000 base. Awaiting formal offer letter. Need to negotiate relocation.'),
    (job_a6, '2025-02-12', 'Phone Screen', 'v2.0', 0,
     'Completed 30-min phone screen with HR. Moving on to take-home coding challenge.'),
    (job_a1, '2025-01-15', 'Applied', 'v1.8', 0, None),
    (job_a3, '2025-02-05', 'Withdrawn', 'v1.9', 1,
     'Withdrew application after accepting preliminary offer from Meridian Health Tech.'),
]

for (jid, dt, status, rv, cl, notes) in apps_a:
    int_data = json.dumps({"notes": notes}) if notes else None
    insert("""INSERT INTO applications (job_id, application_date, status, resume_version,
        cover_letter_sent, interview_data, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (jid, dt, status, rv, cl, int_data, uid_a))

print(f"  → {len(apps_a)} applications inserted for {uname_a}")

# ════════════════════════════════════════════════════════════════════════════
# USER B: Second non-admin (if exists) — Sofia Rivera, UX/product pivot to PM
# ════════════════════════════════════════════════════════════════════════════
if len(non_admins) >= 2:
    uid_b = non_admins[1]['id']
    uname_b = non_admins[1]['username']
    print(f"\nSeeding data for user B: {uname_b} (id={uid_b})")

    co_b1 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        ('Helix Fintech', 'Financial Technology', 'https://helixfintech.com', 'Miami', 'FL',
         'Payments startup. Competitive compensation. Heard good things from former colleague.', uid_b))

    co_b2 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        ('Orion Media Group', 'Digital Media', 'https://orionmediagroup.com', 'New York', 'NY',
         'Digital advertising platform. Product team is small but growing.', uid_b))

    co_b3 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        ('Cascade Cloud', 'Cloud Infrastructure', 'https://cascadecloud.io', 'Seattle', 'WA',
         'Infrastructure as a service. Engineering-led product culture.', uid_b))

    co_b4 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        ('BrightPath EdTech', 'Education Technology', 'https://brightpath.edu', 'Chicago', 'IL',
         'Online learning platform. Mission-driven team. Great PTO policy.', uid_b))

    co_b5 = insert("""INSERT INTO companies (company_name, industry, website, city, state, notes, created_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        ('VaultSec Cybersecurity', 'Cybersecurity', 'https://vaultsec.com', 'San Francisco', 'CA',
         'Series A cybersecurity startup. Referral from former classmate.', uid_b))

    job_b1 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
        job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b1, 'Product Manager', 'Full-time', 105000, 130000,
         'https://helixfintech.com/jobs/pm', '2025-03-10',
         json.dumps(['3+ years PM experience', 'Fintech background preferred', 'Agile/Scrum', 'SQL basics']), uid_b))

    job_b2 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
        job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b2, 'Associate Product Manager', 'Full-time', 90000, 110000,
         'https://orionmediagroup.com/careers/apm', '2025-02-25',
         json.dumps(['1-3 years PM or UX experience', 'Data-driven mindset', 'Familiarity with ad tech']), uid_b))

    job_b3 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
        job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b3, 'Technical Product Manager', 'Full-time', 120000, 150000,
         'https://cascadecloud.io/jobs/tpm', '2025-03-01',
         json.dumps(['Cloud platform experience', 'Engineering background', 'Kubernetes or AWS knowledge']), uid_b))

    job_b4 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
        job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b4, 'Senior UX Designer', 'Full-time', 95000, 115000,
         'https://brightpath.edu/careers/ux', '2025-01-20',
         json.dumps(['Figma', '4+ years UX experience', 'User research', 'Design systems']), uid_b))

    job_b5 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
        job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b5, 'Product Owner', 'Full-time', 100000, 125000,
         'https://vaultsec.com/careers/po', '2025-02-15',
         json.dumps(['Cybersecurity domain knowledge a plus', '3+ years PO experience', 'CSPO certified preferred']), uid_b))

    job_b6 = insert("""INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max,
        job_url, date_posted, requirements, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b1, 'Growth Product Manager', 'Full-time', 110000, 135000,
         'https://helixfintech.com/jobs/gpm', '2025-03-05',
         json.dumps(['A/B testing experience', 'Growth metrics', 'SQL proficiency', 'Python basics']), uid_b))

    # Contacts owned by user B
    insert("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
        linkedin_url, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b1, 'Thomas Nguyen', 'Head of Product', 't.nguyen@helixfintech.com', '555-0201',
         'https://linkedin.com/in/thomasnguyen-product',
         'Coffee chat scheduled. He was impressed by product portfolio. Warm intro via LinkedIn.', uid_b))

    insert("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
        linkedin_url, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b2, 'Rachel Goldstein', 'Senior Recruiter', 'r.goldstein@orionmedia.com', '555-0202',
         'https://linkedin.com/in/rachelgoldstein-hr',
         'Replied quickly. Mentioned team is hiring 3 APMs. Follow up after final round.', uid_b))

    insert("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
        linkedin_url, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b3, 'Alan Park', 'VP of Engineering', 'a.park@cascadecloud.io', '555-0203',
         'https://linkedin.com/in/alanpark-vpe',
         'Former colleague from previous company. Strong internal advocate.', uid_b))

    insert("""INSERT INTO contacts (company_id, contact_name, title, email, phone,
        linkedin_url, notes, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (co_b5, 'Monica Reyes', 'Talent Partner', 'm.reyes@vaultsec.com', '555-0204',
         None, 'Reached out cold. She was receptive and fast-tracked the application.', uid_b))

    apps_b = [
        (job_b1, '2025-03-12', 'Interview', 'v3.0', 1,
         'First round interview completed. Panel of 3. Case study presentation went very well.'),
        (job_b2, '2025-02-27', 'Interview Completed', 'v2.9', 1,
         'Completed 4-round interview process. Waiting on debrief outcome. Strong feedback from team.'),
        (job_b3, '2025-03-03', 'Screening', 'v3.0', 1,
         'Recruiter screen scheduled. Role is senior-level — emphasize cloud background in interview.'),
        (job_b4, '2025-01-22', 'Offer Accepted', 'v2.7', 1,
         'Offer accepted! Start date April 7. Negotiated from $95k to $108k. Excited about the team.'),
        (job_b5, '2025-02-17', 'Phone Screen', 'v2.8', 0,
         'Completed 45-min intro call with Monica. Advancing to take-home product case.'),
        (job_b6, '2025-03-06', 'Applied', 'v3.0', 1, None),
        (job_b2, '2025-01-30', 'Interview Scheduled', 'v2.8', 1,
         'Final round scheduled for Feb 14th. Preparing STAR examples for behavioral questions.'),
        (job_b5, '2024-12-10', 'Withdrawn', 'v2.5', 0,
         'Withdrew prior application. Role requirements did not match. Reapplied to Product Owner role.'),
        (job_b3, '2025-01-10', 'Rejected', 'v2.6', 1,
         'Rejected after first round. Feedback: preferred more infrastructure product experience.'),
    ]

    for (jid, dt, status, rv, cl, notes) in apps_b:
        int_data = json.dumps({"notes": notes}) if notes else None
        insert("""INSERT INTO applications (job_id, application_date, status, resume_version,
            cover_letter_sent, interview_data, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (jid, dt, status, rv, cl, int_data, uid_b))

    print(f"  → {len(apps_b)} applications inserted for {uname_b}")

conn.commit()
conn.close()
print("\nSeed complete!")

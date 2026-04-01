import mysql.connector, os, json
from dotenv import load_dotenv
load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_DATABASE'),
    ssl_ca=os.getenv('SSL_CA_CERT')
)
cur = conn.cursor(dictionary=True)

print("=== Applications per user ===")
cur.execute("""
    SELECT u.username, u.id, COUNT(a.application_id) as app_count
    FROM users u
    LEFT JOIN applications a ON a.user_id = u.id
    GROUP BY u.id, u.username ORDER BY u.id
""")
for r in cur.fetchall():
    print(f"  {r['username']} (id={r['id']}): {r['app_count']} applications")

print("\n=== Companies per user ===")
cur.execute("""
    SELECT u.username, COUNT(c.company_id) as co_count
    FROM users u LEFT JOIN companies c ON c.created_by = u.id
    GROUP BY u.id, u.username ORDER BY u.id
""")
for r in cur.fetchall():
    print(f"  {r['username']}: {r['co_count']} companies")

print("\n=== Jobs per user ===")
cur.execute("""
    SELECT u.username, COUNT(j.job_id) as job_count
    FROM users u LEFT JOIN jobs j ON j.created_by = u.id
    GROUP BY u.id, u.username ORDER BY u.id
""")
for r in cur.fetchall():
    print(f"  {r['username']}: {r['job_count']} jobs")

print("\n=== Contacts per user ===")
cur.execute("""
    SELECT u.username, COUNT(ct.contact_id) as ct_count
    FROM users u LEFT JOIN contacts ct ON ct.created_by = u.id
    GROUP BY u.id, u.username ORDER BY u.id
""")
for r in cur.fetchall():
    print(f"  {r['username']}: {r['ct_count']} contacts")

print("\n=== Application detail for testbot ===")
cur.execute("""
    SELECT a.application_date, a.status, j.job_title, c.company_name
    FROM applications a
    JOIN jobs j ON a.job_id = j.job_id
    JOIN companies c ON j.company_id = c.company_id
    WHERE a.user_id = 2
    ORDER BY a.application_date DESC
""")
for r in cur.fetchall():
    print(f"  {r['application_date']} | {r['status']:25} | {r['job_title']:30} @ {r['company_name']}")

print("\n=== Application detail for tester ===")
cur.execute("""
    SELECT a.application_date, a.status, j.job_title, c.company_name
    FROM applications a
    JOIN jobs j ON a.job_id = j.job_id
    JOIN companies c ON j.company_id = c.company_id
    WHERE a.user_id = 3
    ORDER BY a.application_date DESC
""")
for r in cur.fetchall():
    print(f"  {r['application_date']} | {r['status']:25} | {r['job_title']:30} @ {r['company_name']}")

conn.close()

"""Remove duplicate applications for admin (user_id=1).
Keep the earliest application_id per job_id+status combination."""
import mysql.connector, os
from dotenv import load_dotenv
load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_DATABASE'),
    ssl_ca=os.getenv('SSL_CA_CERT')
)
cur = conn.cursor(dictionary=True)

cur.execute('''
    SELECT job_id, status,
           GROUP_CONCAT(application_id ORDER BY application_id) as ids,
           COUNT(*) as cnt
    FROM applications WHERE user_id = 1
    GROUP BY job_id, status HAVING cnt > 1
''')
dups = cur.fetchall()
print(f"Found {len(dups)} duplicate groups:")

ids_to_delete = []
for d in dups:
    all_ids = list(map(int, d['ids'].split(',')))
    keep = all_ids[0]
    to_del = all_ids[1:]
    print(f"  job_id={d['job_id']} status={d['status']}: KEEP={keep}, DELETE={to_del}")
    ids_to_delete.extend(to_del)

if ids_to_delete:
    placeholders = ','.join(['%s'] * len(ids_to_delete))
    cur.execute(f'DELETE FROM applications WHERE application_id IN ({placeholders})', ids_to_delete)
    print(f"\nDeleted {cur.rowcount} duplicate application(s).")
    conn.commit()
else:
    print("No duplicates found.")

# Verify
cur.execute('SELECT COUNT(*) as total FROM applications WHERE user_id=1')
print(f"Admin applications remaining: {cur.fetchone()['total']}")
cur.execute('SELECT COUNT(*) as total FROM applications')
print(f"Total applications across all users: {cur.fetchone()['total']}")

conn.close()

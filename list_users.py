import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_DATABASE')
)
cur = conn.cursor(dictionary=True)
cur.execute('SELECT id, username, is_admin FROM users ORDER BY id')
for r in cur.fetchall():
    print(r)
conn.close()

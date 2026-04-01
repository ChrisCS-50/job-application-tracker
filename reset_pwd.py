import mysql.connector
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_DATABASE')
)
cursor = conn.cursor()
pwd = generate_password_hash('password123')
cursor.execute("UPDATE users SET password_hash=%s", (pwd,))
conn.commit()
print("All passwords reset to password123")
conn.close()

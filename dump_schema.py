import mysql.connector

try:
    conn = mysql.connector.connect(host='localhost', user='root', password='root', database='job_tracker')
    cursor = conn.cursor(dictionary=True)

    with open('utf8_schemas.txt', 'w', encoding='utf-8') as f:
        for table in ['companies', 'jobs', 'applications', 'contacts']:
            cursor.execute(f"SHOW CREATE TABLE {table}")
            res = cursor.fetchone()
            f.write(f"--- {table} ---\n")
            f.write(res['Create Table'] + "\n\n")

    print('Schemas dumped successfully!')
except Exception as e:
    print(e)

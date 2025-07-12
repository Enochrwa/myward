import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("DB_HOST")
port = int(os.getenv("DB_PORT", "16628"))
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")  # Must NOT be None or empty

print(f"Connecting to {host}:{port} as {user}")
print("Password loaded:", "YES" if password else "NO")  # Debug

connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    db="defaultdb",  # change if needed
    port=port,
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    connect_timeout=10,
    read_timeout=10,
    write_timeout=10,
)

try:
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS mytest (id INTEGER PRIMARY KEY)")
        cursor.execute("INSERT INTO mytest (id) VALUES (1), (2)")
        connection.commit()
        cursor.execute("SELECT * FROM mytest")
        print(cursor.fetchall())
finally:
    connection.close()

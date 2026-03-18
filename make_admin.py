import sqlite3
import os

db_path = os.path.join('instance', 'ecommerce.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("UPDATE user SET is_admin = 1 WHERE email = 'testuser@example.com'")
conn.commit()
conn.close()
print("testuser is now an admin")

import sqlite3
conn = sqlite3.connect('/opt/data/state.db')
c = conn.cursor()
c.execute("SELECT * FROM state_meta;")
rows = c.fetchall()
print(rows)
conn.close()

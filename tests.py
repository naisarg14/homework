#Merge two databases

import sqlite3

conn1 = sqlite3.connect('homework.db')
conn2 = sqlite3.connect('homework2.db')

cursor1 = conn1.cursor()
cursor2 = conn2.cursor()

cursor2.execute('SELECT * FROM worksheet')
rows = cursor2.fetchall()

for row in rows:
    #row = row + ("none", )
    cursor1.execute('INSERT OR IGNORE INTO worksheet VALUES (?, ?, ?, ?, ?, ?, ?, ?)', row)

conn1.commit()
conn2.close()
conn1.close()


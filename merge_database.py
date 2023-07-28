#Merge two databases

import sqlite3

conn1 = sqlite3.connect('homework.db')
conn2 = sqlite3.connect('homework2.db')

cursor1 = conn1.cursor()
cursor2 = conn2.cursor()

for table in ["homework", "exam", "outline", "timetable", "guest", "worksheet"]:
    cursor2.execute('SELECT * FROM ?', table)
    rows = cursor2.fetchall()

    for row in rows:
        try:
            cursor1.execute('INSERT OR IGNORE INTO ? VALUES (?, ?, ?, ?, ?, ?, ?, ?)', table, row)
        except:
            row = row + ("none", )
            cursor1.execute('INSERT OR IGNORE INTO ? VALUES (?, ?, ?, ?, ?, ?, ?, ?)', table, row)


conn1.commit()
conn2.close()
conn1.close()


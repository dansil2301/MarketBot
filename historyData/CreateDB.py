import sqlite3

conn = sqlite3.connect('HistoryData.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS historyData (
        id INTEGER PRIMARY KEY,
        open float NOT NULL,
        close float NOT NULL,
        high float NOT NULL,
        low float NOT NULL,
        volume bigint NOT NULL,
        time datetime NOT NULL,
        is_completed binary NOT NULL
    )
''')

conn.commit()
conn.close()


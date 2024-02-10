import sqlite3

conn = sqlite3.connect('HistoryData.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS historyDataHour(
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS historyData15Minutes(
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS historyData10Minutes(
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


cursor.execute('''
    CREATE TABLE IF NOT EXISTS historyData5Minutes(
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS historyData1Minute(
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


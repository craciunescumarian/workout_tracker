import sqlite3

def create_connection():
    conn = sqlite3.connect('gym_tracker.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value INTEGER NOT NULL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()

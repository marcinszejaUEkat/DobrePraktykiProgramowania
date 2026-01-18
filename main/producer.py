import sqlite3
import uuid
import sys
import os

# 1. DEFINICJA ŚCIEŻKI (To musi być na górze)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'queue.db')


def init_db():
    # 2. UŻYCIE ZMIENNEJ DB_NAME (A nie 'queue.db')
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS tasks
                   (
                       id
                       TEXT
                       PRIMARY
                       KEY,
                       status
                       TEXT
                       NOT
                       NULL
                   )
                   ''')
    conn.commit()
    conn.close()


def add_task():
    task_id = str(uuid.uuid4())
    status = 'pending'

    # 3. UŻYCIE ZMIENNEJ DB_NAME TUTAJ TEŻ
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO tasks (id, status) VALUES (?, ?)", (task_id, status))
    conn.commit()
    conn.close()

    print(f"Dodano zadanie: {task_id} ze statusem {status}")


if __name__ == "__main__":
    init_db()
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        for _ in range(100):
            add_task()
    else:
        add_task()
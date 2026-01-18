import sqlite3
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'queue.db')

WORK_DURATION = 30
CHECK_INTERVAL = 5


def process_tasks():
    while True:
        task_id = None

        try:
            with sqlite3.connect(DB_NAME, timeout=10) as conn:
                conn.isolation_level = 'IMMEDIATE'
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM tasks WHERE status = 'pending' LIMIT 1")
                row = cursor.fetchone()

                if row:
                    task_id = row[0]
                    cursor.execute("UPDATE tasks SET status = 'in progress' WHERE id = ?", (task_id,))
        except sqlite3.OperationalError:
            print("Baza zablokowana, ponawiam...")
            time.sleep(1)
            continue

        if task_id:
            print(f"Pobrano zadanie {task_id}. Przetwarzanie przez {WORK_DURATION}s...")
            time.sleep(WORK_DURATION)

            with sqlite3.connect(DB_NAME, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (task_id,))
                print(f"Zadanie {task_id} zakończone.")
        else:
            print("Brak zadań. Oczekiwanie...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    print("Uruchamianie konsumenta SQLite...")
    process_tasks()
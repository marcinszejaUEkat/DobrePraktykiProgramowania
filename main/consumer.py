import sqlite3
import time
import os

# 1. DEFINICJA ŚCIEŻKI (To musi być na górze)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'queue.db')

WORK_DURATION = 30  # Czas trwania pracy w sekundach
CHECK_INTERVAL = 5  # Czas oczekiwania, gdy brak zadań


def process_tasks():
    while True:
        task_id = None

        # KROK 1: Pobranie zadania (Transakcja)
        try:
            # Używamy context managera, który automatycznie robi commit/rollback
            with sqlite3.connect(DB_NAME, timeout=10) as conn:
                # Ustawiamy izolację transakcji na IMMEDIATE, aby zablokować bazę dla zapisu
                # w momencie rozpoczęcia transakcji (zapobiega konfliktom wielu konsumentów)
                conn.isolation_level = 'IMMEDIATE'
                cursor = conn.cursor()

                # Znajdź jedno zadanie ze statusem 'pending'
                cursor.execute("SELECT id FROM tasks WHERE status = 'pending' LIMIT 1")
                row = cursor.fetchone()

                if row:
                    task_id = row[0]
                    # Zmień status na 'in progress'
                    cursor.execute("UPDATE tasks SET status = 'in progress' WHERE id = ?", (task_id,))
                    # Transakcja kończy się tutaj (commit automatyczny przy wyjściu z bloku with)
        except sqlite3.OperationalError:
            # Czasami baza może być zablokowana przez innego konsumenta, ponawiamy próbę
            print("Baza zablokowana, ponawiam...")
            time.sleep(1)
            continue

        # KROK 2: Wykonanie pracy (poza transakcją bazy danych!)
        if task_id:
            print(f"Pobrano zadanie {task_id}. Przetwarzanie przez {WORK_DURATION}s...")
            time.sleep(WORK_DURATION)  # Symulacja pracy

            # KROK 3: Zmiana statusu na 'done'
            with sqlite3.connect(DB_NAME, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (task_id,))
                print(f"Zadanie {task_id} zakończone.")
        else:
            print("Brak zadań. Oczekiwanie...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    print("Uruchamianie konsumenta SQLite...")
    # Upewniamy się, że baza istnieje (na wypadek uruchomienia consumer przed producer)
    # W prostym skrypcie można duplikować init lub założyć, że producer był pierwszy.
    process_tasks()
import csv
import time
import os
import shutil
from tempfile import NamedTemporaryFile

QUEUE_FILE = 'tasks.csv'
WORK_DURATION = 30  # Czas trwania pracy w sekundach
CHECK_INTERVAL = 5  # Interwał sprawdzania pliku


def process_tasks():
    while True:
        task_to_process = None

        # KROK 1: Odczyt i "Zarezerwowanie" zadania (zmiana na in progress)
        # Musimy to zrobić atomowo-podobnie, czytając i zapisując plik tymczasowy
        if os.path.exists(QUEUE_FILE):
            temp_file = NamedTemporaryFile(mode='w', delete=False, newline='')

            with open(QUEUE_FILE, 'r') as csvfile, temp_file:
                reader = csv.DictReader(csvfile)
                fieldnames = ['id', 'status']
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    # Znajdź pierwsze zadanie pending, które nie jest jeszcze procesowane
                    if row['status'] == 'pending' and task_to_process is None:
                        row['status'] = 'in progress'  # Zmiana statusu na in progress
                        task_to_process = row

                    writer.writerow(row)

            # Podmieniamy plik oryginalny plikiem tymczasowym (zaktualizowanym)
            shutil.move(temp_file.name, QUEUE_FILE)

        # KROK 2: Wykonanie pracy
        if task_to_process:
            print(f"Pobrano zadanie {task_to_process['id']}. Przetwarzanie przez {WORK_DURATION}s...")
            time.sleep(WORK_DURATION)  # Symulacja pracy

            # KROK 3: Zmiana statusu na done po wykonaniu
            temp_file = NamedTemporaryFile(mode='w', delete=False, newline='')
            with open(QUEUE_FILE, 'r') as csvfile, temp_file:
                reader = csv.DictReader(csvfile)
                fieldnames = ['id', 'status']
                writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    if row['id'] == task_to_process['id']:
                        row['status'] = 'done'  # Zmiana statusu na done
                        print(f"Zadanie {row['id']} zakończone.")
                    writer.writerow(row)

            shutil.move(temp_file.name, QUEUE_FILE)

            # Po wykonaniu zadania, sprawdzamy od razu czy są następne,
            # czy czekamy? Instrukcja mówi "stale uruchomiony", więc pętla leci dalej.
        else:
            print("Brak zadań. Oczekiwanie...")
            time.sleep(CHECK_INTERVAL)  # Czekamy 5s przed kolejnym sprawdzeniem


if __name__ == "__main__":
    print("Uruchamianie konsumenta...")
    process_tasks()
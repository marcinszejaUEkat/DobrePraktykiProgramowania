import csv
import uuid
import os
import sys

QUEUE_FILE = 'tasks.csv'


def add_task():
    # Sprawdzamy, czy plik istnieje, aby dodać nagłówki
    file_exists = os.path.isfile(QUEUE_FILE)

    task_id = str(uuid.uuid4())
    status = 'pending'

    with open(QUEUE_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Jeśli plik jest nowy, dodajemy nagłówki
        if not file_exists:
            writer.writerow(['id', 'status'])

        # Zapisujemy zadanie (status pending)
        writer.writerow([task_id, status])
        print(f"Dodano zadanie: {task_id} ze statusem {status}")


if __name__ == "__main__":
    # Opcjonalnie: pętla do dodania 100 zadań na raz,
    # jeśli uruchomimy z argumentem 'batch', w przeciwnym razie dodaje 1.
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        for _ in range(100):
            add_task()
    else:
        add_task()
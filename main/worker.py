import pika
import json
import time
import sys
import os

# Dodajemy katalog bieżący do ścieżki, żeby widzieć utils.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import count_people_in_image

RABBIT_HOST = 'localhost'
QUEUE_NAME = 'image_analysis_queue'


def process_message(ch, method, properties, body):
    """Funkcja wywoływana dla każdego zadania z kolejki."""
    try:
        data = json.loads(body)
        url = data.get("url")

        print(f" [x] Odebrano URL: {url}")

        # --- Wykonanie ciężkiej pracy ---
        start_time = time.time()
        count = count_people_in_image(url)
        duration = time.time() - start_time
        # --------------------------------

        print(f" [V] Wynik: {count} osób. Czas: {duration:.2f}s")

    except Exception as e:
        print(f" [!] Błąd przetwarzania wiadomości: {e}")
    finally:
        # Bardzo ważne: Potwierdzenie wykonania zadania (ACK)
        # Bez tego RabbitMQ wyśle zadanie ponownie!
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    while True:
        try:
            CLOUDAMQP_URL = "amqps://mgpscvpi:Y96Nr8btFbCevNfU-otLLjDkvqv7SOGg@kebnekaise.lmq.cloudamqp.com/mgpscvpi"
            params = pika.URLParameters(CLOUDAMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            # Deklaracja kolejki (musi być taka sama jak w producerze)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            # Worker bierze tylko 1 zadanie na raz (nie bierze na zapas)
            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)

            print(' [*] Worker wystartował. Czekam na zdjęcia...')
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            print("Brak połączenia z RabbitMQ. Ponawiam za 5s...")
            time.sleep(5)


if __name__ == "__main__":
    try:
        start_worker()
    except KeyboardInterrupt:
        print("Zatrzymano workera.")
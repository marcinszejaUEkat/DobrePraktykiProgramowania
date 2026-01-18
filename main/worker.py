import pika
import json
import time
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

RABBIT_HOST = 'localhost'
QUEUE_NAME = 'image_analysis_queue'

SERVICE_A_URL = "http://127.0.0.1:8001/results"


def process_message(ch, method, properties, body):
    try:
        data = json.loads(body)
        url = data.get("url")

        print(f" [x] Pobrano URL: {url}")

        start_time = time.time()

        from utils import count_people_in_image
        count = count_people_in_image(url)
        duration = time.time() - start_time


        payload = {
            "url": url,
            "person_count": count,
            "processing_time": duration
        }

        print(f" [>] Wysyłanie do Serwisu A...")
        response = requests.post(SERVICE_A_URL, json=payload, timeout=5)

        response.raise_for_status()

        print(" [V] Sukces! Wynik zapisany w Serwisie A.")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except requests.exceptions.RequestException as e:
        print(f" [!] Błąd połączenia z Serwisem A: {e}")
        print(" [!] Nie potwierdzam wiadomości (NACK). Zadanie wróci do kolejki.")
        time.sleep(5)

    except Exception as e:
        print(f" [!] Inny błąd krytyczny: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    while True:
        try:
            CLOUDAMQP_URL = "amqps://mgpscvpi:Y96Nr8btFbCevNfU-otLLjDkvqv7SOGg@kebnekaise.lmq.cloudamqp.com/mgpscvpi"
            params = pika.URLParameters(CLOUDAMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.queue_declare(queue=QUEUE_NAME, durable=True)

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
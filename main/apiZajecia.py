from fastapi import FastAPI
from pydantic import BaseModel
import pika
import json

app = FastAPI()


# Model danych wejściowych
class ImageRequest(BaseModel):
    url: str


# Funkcja pomocnicza do wysyłania wiadomości
def send_to_rabbitmq(url: str):
    CLOUDAMQP_URL = "amqps://mgpscvpi:Y96Nr8btFbCevNfU-otLLjDkvqv7SOGg@kebnekaise.lmq.cloudamqp.com/mgpscvpi"
    params = pika.URLParameters(CLOUDAMQP_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Deklaracja kolejki
    channel.queue_declare(queue='image_analysis_queue', durable=True)

    message = json.dumps({"url": url})

    channel.basic_publish(
        exchange='',
        routing_key='image_analysis_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    connection.close()


@app.post("/analyze_img", status_code=202)
def analyze_image_endpoint(request: ImageRequest):
    """
    Endpoint asynchroniczny:
    1. Przyjmuje URL.
    2. Wrzuca go do RabbitMQ.
    3. Zwraca natychmiast potwierdzenie przyjęcia (202 Accepted).
    """
    send_to_rabbitmq(request.url)

    return {
        "message": "Zadanie przyjęte do analizy",
        "url": request.url,
        "status": "queued"
    }
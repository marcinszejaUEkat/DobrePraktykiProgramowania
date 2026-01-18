import cv2
import numpy as np
import requests
import os

# Ścieżki do plików TensorFlow
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "frozen_inference_graph.pb")
CONFIG_PATH = os.path.join(BASE_DIR, "ssd_mobilenet_v2_coco_2018_03_29.pbtxt")


def count_people_in_image(image_url: str) -> int:
    """
    Zlicza osoby używając modelu TensorFlow (SSD MobileNet V2) wczytanego przez OpenCV.
    """
    try:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(CONFIG_PATH):
            print("Błąd: Brakuje plików modelu TensorFlow!")
            return 0

        # 1. Pobranie obrazu
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()

        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return 0

        # 2. Wczytanie sieci TensorFlow (zgodnie z Wiki OpenCV)
        net = cv2.dnn.readNetFromTensorflow(MODEL_PATH, CONFIG_PATH)

        # 3. Przygotowanie Bloba (Image Preprocessing)
        # TensorFlow oczekuje: size=(300,300), swapRB=True (bo OpenCV ma BGR, a model chce RGB)
        blob = cv2.dnn.blobFromImage(image, size=(300, 300), swapRB=True, crop=False)
        net.setInput(blob)

        # 4. Detekcja
        detections = net.forward()

        person_count = 0

        # 5. Iteracja po wynikach
        # detections[0, 0, i, 1] -> Klasa (1 = person w zbiorze COCO dla tego modelu)
        # detections[0, 0, i, 2] -> Pewność (Confidence)
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.4:  # Próg pewności 40%
                class_id = int(detections[0, 0, i, 1])

                # W modelu COCO klasa 1 to zazwyczaj 'person'
                if class_id == 1:
                    person_count += 1

        return person_count

    except Exception as e:
        print(f"Błąd TensorFlow/OpenCV: {e}")
        return 0
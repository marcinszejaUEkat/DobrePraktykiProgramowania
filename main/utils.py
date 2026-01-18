import cv2
import numpy as np
import requests
import os

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

        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()

        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return 0

        net = cv2.dnn.readNetFromTensorflow(MODEL_PATH, CONFIG_PATH)

        blob = cv2.dnn.blobFromImage(image, size=(300, 300), swapRB=True, crop=False)
        net.setInput(blob)

        detections = net.forward()

        person_count = 0

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.4:
                class_id = int(detections[0, 0, i, 1])

                if class_id == 1:
                    person_count += 1

        return person_count

    except Exception as e:
        print(f"Błąd TensorFlow/OpenCV: {e}")
        return 0
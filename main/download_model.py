import urllib.request
import os
import tarfile

# Linki do oficjalnego modelu TensorFlow (SSD MobileNet V2)
MODEL_URL = "http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz"
CONFIG_URL = "https://raw.githubusercontent.com/opencv/opencv_extra/master/testdata/dnn/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"


def download_files():
    print("Pobieranie modelu TensorFlow (zgodnie z OpenCV Wiki)...")

    # 1. Pobieranie archiwum z modelem
    if not os.path.exists("ssd_mobilenet_v2_coco.tar.gz"):
        print("Pobieranie tar.gz...")
        urllib.request.urlretrieve(MODEL_URL, "ssd_mobilenet_v2_coco.tar.gz")

    # 2. Rozpakowanie pliku .pb (frozen graph)
    print("Rozpakowywanie modelu...")
    with tarfile.open("ssd_mobilenet_v2_coco.tar.gz", "r:gz") as tar:
        # Szukamy pliku frozen_inference_graph.pb wewnątrz archiwum
        member = tar.getmember("ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb")
        member.name = "frozen_inference_graph.pb"  # Zmieniamy nazwę na krótszą
        tar.extract(member, path=".")

    # 3. Pobieranie pliku konfiguracyjnego .pbtxt (wymagany przez OpenCV dla modeli TF)
    if not os.path.exists("ssd_mobilenet_v2_coco_2018_03_29.pbtxt"):
        print("Pobieranie pliku config .pbtxt...")
        urllib.request.urlretrieve(CONFIG_URL, "ssd_mobilenet_v2_coco_2018_03_29.pbtxt")

    print("Gotowe! Masz pliki: frozen_inference_graph.pb oraz ssd_mobilenet_v2_coco_2018_03_29.pbtxt")


if __name__ == "__main__":
    download_files()
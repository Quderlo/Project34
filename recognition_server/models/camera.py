import numpy
import cv2
import requests

from app_config import DjangoServer
from recognition_server.models.face_processor import FaceProcessor
from recognition_server.utils.authenticate import login_and_get_session


class Camera(object):
    def __init__(self, pk, url):
        self.pk = pk
        self.url = url
        self.is_active = False
        self.session = requests.Session()
        self.processor = FaceProcessor()
        self.api_endpoint = DjangoServer.url + DjangoServer.endpoints['access']  # Измените на ваш endpoint

    def fetch_and_process(self):
        try:
            # Получение кадра
            response = self.session.get(self.url, timeout=2)
            if response.status_code != 200:
                return False

            image = cv2.imdecode(numpy.frombuffer(response.content, numpy.uint8), cv2.IMREAD_COLOR)

            # Обработка кадра
            face_data_list = self.processor.process_frame(image)

            # Отправка данных для каждого обнаруженного лица
            for face_data_b64 in face_data_list:
                self.send_data(face_data_b64)

            return True

        except Exception as e:
            print(f"Camera {self.pk} error: {str(e)}")
            return False

    def send_data(self, face_data_b64):
        """Отправка данных на API"""
        try:
            payload = {
                "face_data": face_data_b64,
                "camera_id": self.pk
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers=headers,
                timeout=3,
                cookies=login_and_get_session(),
            )

            if response.status_code == 201:
                print(f"Data sent successfully for camera {self.pk}")
            else:
                print(f"API Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"API Connection Error: {str(e)}")
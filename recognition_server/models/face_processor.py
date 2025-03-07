import base64

import dlib
import cv2
import numpy as np


class FaceProcessor:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.sp = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

    def process_frame(self, image):
        """Обработка кадра и возврат данных для отправки"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detections = self.detector(rgb_image, 1)

        results = []
        for detection in detections:
            shape = self.sp(rgb_image, detection)
            descriptor = self.facerec.compute_face_descriptor(rgb_image, shape)

            # Конвертация дескриптора в бинарный формат и base64
            descriptor_bytes = np.array(descriptor, dtype=np.float32).tobytes()
            face_data_b64 = base64.b64encode(descriptor_bytes).decode('utf-8')

            results.append(face_data_b64)

        return results
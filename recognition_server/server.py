import threading
import time
import cv2

from recognition_server.models.camera import Camera
from recognition_server.utils.get_data import get_camera_urls


class Server:
    def __init__(self):
        self.cameras = []
        self.threads = {}
        self.lock = threading.Lock()
        self.poll_interval = 1  # Интервал опроса камер в секундах
        self.initialize_cameras()
        print('Server initialized')

    def initialize_cameras(self):
        current_cameras = get_camera_urls()
        current_ids = {cam['id'] for cam in current_cameras}

        # Удаление неактуальных камер
        with self.lock:
            for camera in self.cameras[:]:
                if camera.pk not in current_ids:
                    camera.is_active = False
                    self.cameras.remove(camera)
                    print(f"Camera {camera.pk} removed")

        existing_ids = {cam.pk for cam in self.cameras}
        for cam_data in current_cameras:
            if cam_data['id'] not in existing_ids:
                new_cam = Camera(pk=cam_data['id'], url=cam_data['url'])
                new_cam.is_active = True
                self.cameras.append(new_cam)
                print(f"Camera {new_cam.pk} added")
                self.start_camera_thread(new_cam)

    def start_camera_thread(self, camera):
        def poll_camera():
            while camera.is_active:
                start_time = time.time()
                camera.fetch_and_process()

                elapsed = time.time() - start_time
                sleep_time = max(0, self.poll_interval - elapsed)
                time.sleep(sleep_time)

        thread = threading.Thread(target=poll_camera, daemon=True)
        thread.start()
        self.threads[camera.pk] = thread

    def shutdown(self):
        """Завершение работы сервера"""
        with self.lock:
            # Остановка всех камер
            for camera in self.cameras:
                camera.is_active = False

            # Ожидание завершения потоков
            for thread in self.threads.values():
                thread.join()

            self.cameras.clear()
            self.threads.clear()

        # Закрытие всех окон OpenCV
        cv2.destroyAllWindows()
        print("Server shutdown complete")
import requests

from app_config import DjangoServer
from recognition_server.utils.authenticate import login_and_get_session


def get_camera_urls() -> list[dict]:
    """
    Получает данные о камерах с API и извлекает ID и RTSP-ссылку
    Возвращает список словарей вида [{'id': int, 'rtsp_link': str}]
    """

    cookie = login_and_get_session()

    url = DjangoServer.url + DjangoServer.endpoints['camera']

    try:
        response = requests.get(url, timeout=5, cookies=cookie)
        response.raise_for_status()

        cameras_data = response.json()


        return [
            {
                "id": cam["id"],
                "url": cam["image_link"]
            }
            for cam in cameras_data
            if "id" in cam and "image_link" in cam
        ]

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {str(e)}")
        return []
    except ValueError as e:
        print(f"Ошибка парсинга JSON: {str(e)}")
        return []
    except KeyError as e:
        print(f"Отсутствует обязательное поле в данных: {str(e)}")
        return []

import requests

def get_camera_urls() -> list[dict]:
    """
    Получает данные о камерах с API и извлекает ID и RTSP-ссылку
    Возвращает список словарей вида [{'id': int, 'rtsp_link': str}]
    """
    try:
        response = requests.get('http://127.0.0.1:8000/camera', timeout=5)
        response.raise_for_status()

        cameras_data = response.json()

        return [
            {
                "id": cam["id"],
                "rtsp_link": cam["rtsp_link"]
            }
            for cam in cameras_data
            if "id" in cam and "rtsp_link" in cam
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

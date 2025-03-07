from typing import Dict

import requests

from app_config import DjangoServer


def login_and_get_session(data : dict = None) -> Dict | None:
    """
    Авторизуется на сервере и возвращает session_id
    Возвращает:
    Dict
        session_id (str) - идентификатор сессии
        csrf_token (str) - токен
        None - если авторизация не удалась
    """

    url = DjangoServer.url + DjangoServer.endpoints['login']

    if not data:
        data = DjangoServer.auth

    with requests.Session() as session:

        try:
            response = session.post(
                url,
                data=data,
                timeout=5
            )

            # Проверка успешного ответа
            if response.status_code == 200:
                session_id = session.cookies.get('sessionid')
                csrf_token = session.cookies.get('csrftoken')
                auth_data = {
                    'csrftoken': csrf_token,
                    'sessionid': session_id,
                }
                return auth_data

            print(f"Ошибка авторизации: {response.status_code}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения: {str(e)}")
            return None

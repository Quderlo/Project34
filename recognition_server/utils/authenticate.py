import requests


def login_and_get_session(data: dict) -> str:
    """
    Авторизуется на сервере и возвращает session_id
    Возвращает:
        session_id (str) - идентификатор сессии
        None - если авторизация не удалась
    """
    with requests.Session() as session:
        try:
            response = session.post(
                "http://127.0.0.1:8000/login/",
                data=data,
                timeout=5
            )

            # Проверка успешного ответа
            if response.status_code == 200:
                session_id = session.cookies.get('sessionid') or session.cookies.get('session_id')
                return session_id

            print(f"Ошибка авторизации: {response.status_code}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения: {str(e)}")
            return None


data = {'username': 'test', 'password': 'test'}
session_id = login_and_get_session(data)

if session_id:
    print(f"Успешная авторизация! Session ID: {session_id}")
else:
    print("Авторизация не удалась")
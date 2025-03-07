class DjangoServer():
    ip = '127.0.0.1'
    port = 8000
    url = f'http://{ip}:{port}'
    auth = {
        'username': 'admin',
        'password': 'admin',
    }

    endpoints = {
        'camera': '/camera', # GET
        'access': '/access/', # POST
        'login': '/login/', # POST
    }


class FastApiServer():
    ip = '127.0.0.1'
    port = 8001
    url = f'http://{ip}:{port}'
    endpoints = {
        'refresh': '/refresh/', # POST
    }
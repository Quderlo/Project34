import datetime
from contextlib import asynccontextmanager

import cv2
import uvicorn
from fastapi import FastAPI, BackgroundTasks

from app_config import FastApiServer
from recognition_server.server import Server

server = Server()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f'Server start {datetime.datetime.now()}')
    yield
    print(f'Server stop {datetime.datetime.now()}')

    server.shutdown()
    cv2.destroyAllWindows()


app = FastAPI(lifespan=lifespan)

@app.post(f'{FastApiServer.endpoints['refresh']}')
async def refresh(background_tasks: BackgroundTasks):
    """
    Эндпоинт обновления списка камер
    """
    server.initialize_cameras()


if __name__ == '__main__':
    uvicorn.run(app, host=FastApiServer.ip, port=FastApiServer.port)


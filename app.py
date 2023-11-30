from website import create_app
from website.API.fastapi import fastapi_app

app = create_app()


if __name__ == '__main__':
    from threading import Thread
    from uvicorn import run as uvicorn_run

    # Start Flask in a separate thread
    def start_flask():
        app.run(host='0.0.0.0', port=8000)

    flask_thread = Thread(target=start_flask)
    flask_thread.start()

    # Start FastAPI using Uvicorn
    uvicorn_run(fastapi_app, host='127.0.0.1', port=7000)

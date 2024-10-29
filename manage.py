from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    app.run(host=Config.LISTEN_TO_HOSTS, port=Config.FLASK_PORT)
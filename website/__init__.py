from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()
# SECRET KEY GEN:
#   import uuid
#   uuid.uuid4().hex
# OR
#   import secrets
#   secrets.token_urlsafe(12)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app
    
from flask import Flask

# SECRET KEY GEN:
#   import uuid
#   uuid.uuid4().hex
# OR
#   import secrets
#   secrets.token_urlsafe(12)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'db8ec40dda154bd4a75b85021b1708a0'
    
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app
    
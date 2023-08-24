from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hajsaksdl laksjdwlfk'
    
    from .views import views
    from .auth import auth
    from .config import conn
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app
    
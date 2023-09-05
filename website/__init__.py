from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

import os
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # CONFIGURING POSTGRESQL CONNECTIONS
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # LOADING DATABASE 
    from website.models import init_db
    init_db(app)
    
    # LOADING MODEL CLASSES
    from .models import Admin,Faculty,Faculty_Data,Faculty_Profile,Student 
    
    # IMPORTING ROUTES
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # LOADING LOGIN MANAGER CACHE
    login_manager = LoginManager()
    login_manager.login_view = 'auth.faculty_denied'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Faculty_Profile.query.get(int(user_id))
    
    return app
    
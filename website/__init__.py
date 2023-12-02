from flask import Flask, session
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_mail import Mail
from datetime import timedelta
from flask_jwt_extended import JWTManager

import os
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['REFRESH_TOKEN_SECRET'] = os.getenv('REFRESH_TOKEN_SECRET')
    
    # CONFIGURING POSTGRESQL CONNECTIONS
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}  
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
    
    # SMTP CONFIGURATION

    app.config["MAIL_SERVER"]=os.getenv("MAILSERVER") 
    app.config["MAIL_PORT"]=os.getenv("MAILPORT") 
    app.config["MAIL_USERNAME"] = os.getenv("FISGMAIL")     
    app.config['MAIL_PASSWORD'] = os.getenv("FISGMAILPASS") 
    app.config['MAIL_DEFAULT_SENDER'] = 'PUPQC FIS'               
    app.config['MAIL_USE_TLS']=os.getenv("TLS") 
    app.config['MAIL_USE_SSL']=os.getenv("SSL") 
    
    
    # UPLOAD CONFIGURATION
    app.config['IMAGE_UPLOADS']='temp/'
    
    mail=Mail(app)
  
    # LOADING DATABASE 
    from .models import init_db
    init_db(app)
    
    # LOADING MODEL CLASSES
    from .models import Faculty_Profile
    
    # IMPORTING ROUTES
    from .views import views
    from .auth import auth
    from .API.api_app import API
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(API, url_prefix='/')
    
     # IMPORTING MODULES
    from .modules.PDM import PDM
    app.register_blueprint(PDM, url_prefix='/')
    
    # LOADING LOGIN MANAGER CACHE
    login_manager = LoginManager()
    login_manager.login_view = 'auth.faculty_denied'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Faculty_Profile.query.get(str(user_id))
    
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        session.modified = True
    
    return app
    
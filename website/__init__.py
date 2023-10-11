from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_mail import Mail

import os
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    # CONFIGURING POSTGRESQL CONNECTIONS
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # SMTP CONFIGURATION

    app.config["MAIL_SERVER"]='smtp.gmail.com'
    app.config["MAIL_PORT"]=465
    app.config["MAIL_USERNAME"] = os.getenv("FISGMAIL")     
    app.config['MAIL_PASSWORD'] = os.getenv("FISGMAILPASS") 
    app.config['MAIL_DEFAULT_SENDER'] = 'PUPQC FIS'               
    app.config['MAIL_USE_TLS']=False
    app.config['MAIL_USE_SSL']=True

    mail=Mail(app)
        
    # LOADING DATABASE 
    from website.models import init_db
    init_db(app)
    
    # LOADING MODEL CLASSES
    from .models import Faculty_Profile
    
    # IMPORTING ROUTES
    from .views import views
    from .auth import auth
    from .API.api_routes import API
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(API, url_prefix='/')
    
    # LOADING LOGIN MANAGER CACHE
    login_manager = LoginManager()
    login_manager.login_view = 'auth.faculty_denied'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return Faculty_Profile.query.get(int(user_id))
    
    return app
    
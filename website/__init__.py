from flask import Flask, session
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_mail import Mail
from datetime import timedelta

import os
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.json.sort_keys = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
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
    app.config['MAIL_USE_TLS']=False
    app.config['MAIL_USE_SSL']=True
    
    mail=Mail(app)
        
    # LOADING DATABASE 
    from website.models import init_db
    init_db(app)
    
    # LOADING MODEL CLASSES
    from .models import Faculty_Profile
    
        # LOADING MODEL PDS_TABLES
    from .models import PDS_Personal_Details, PDS_Contact_Details, PDS_Family_Background, PDS_Educational_Background, PDS_Eligibity, PDS_Work_Experience, PDS_Voluntary_Work, PDS_Training_Seminars, PDS_Outstanding_Achievements, PDS_OfficeShips_Memberships, PDS_Agency_Membership, PDS_Teacher_Information, PDS_Additional_Questions, PDS_Character_Reference,PDS_Signature
    
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
        return Faculty_Profile.query.get(str(user_id))
    
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        session.modified = True
    
    return app
    